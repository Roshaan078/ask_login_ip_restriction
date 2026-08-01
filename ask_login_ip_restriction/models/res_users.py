import logging
from werkzeug.exceptions import Unauthorized
from odoo import models, fields, api, exceptions
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    ip_restriction_ids = fields.One2many(
        'user.ip.restriction',
        'user_id',
        string='Allowed IP Addresses',
        help='Leave empty to allow login from any IP',
    )
    enable_ip_restriction = fields.Boolean(
        string='Enable IP Restriction',
        default=False,
        help='Enable IP-based login restriction for this user',
    )

    @api.model
    def _get_client_ip(self):
        """Extract client IP from request headers"""
        if not request:
            return None

        # Try multiple headers for IP detection
        if request.httprequest.headers.get('CF-Connecting-IP'):
            # Cloudflare
            return request.httprequest.headers.get('CF-Connecting-IP')
        elif request.httprequest.headers.get('X-Forwarded-For'):
            # Multiple proxies - take first
            return request.httprequest.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.httprequest.headers.get('X-Real-IP'):
            # Nginx proxy
            return request.httprequest.headers.get('X-Real-IP')
        else:
            # Direct connection
            return request.httprequest.remote_addr

    @api.model
    def authenticate(self, db, login, password, user_agent_env=None):
        """Override authenticate to check IP restriction"""
        uid = super().authenticate(db, login, password, user_agent_env)

        if not uid:
            return uid

        # Get user
        user = self.browse(uid)

        # Check IP restriction only if enabled
        if user.enable_ip_restriction and user.ip_restriction_ids:
            client_ip = self._get_client_ip()

            if not client_ip:
                _logger.warning(
                    f"Could not determine client IP for user {user.login}"
                )
                raise exceptions.AccessDenied(
                    "Could not determine your IP address. "
                    "IP restriction is enabled but verification failed."
                )

            # Check IP restriction
            is_allowed, message = self.env['user.ip.restriction']._check_ip_restriction(
                uid, client_ip
            )

            if not is_allowed:
                _logger.warning(
                    f"Login attempt from unauthorized IP {client_ip} for user {user.login}"
                )
                raise exceptions.AccessDenied(
                    f"Login not allowed from your IP address ({client_ip}). "
                    "Contact your administrator."
                )

            _logger.info(
                f"User {user.login} authenticated from IP {client_ip}"
            )

        return uid

    @api.model
    def check_credentials(self, password, user_agent_env=None):
        """Override check_credentials for additional validation"""
        try:
            return super().check_credentials(password, user_agent_env)
        except exceptions.AccessDenied as e:
            # Re-raise with proper formatting
            raise

    def action_reset_ip_restrictions(self):
        """Action to reset all IP restrictions for user"""
        self.ensure_one()
        self.ip_restriction_ids.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'All IP restrictions have been removed.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_add_current_ip(self):
        """Action to add current IP to restrictions"""
        self.ensure_one()
        client_ip = self._get_client_ip()

        if not client_ip:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Could not determine your IP address.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

        # Check if IP already exists
        existing = self.env['user.ip.restriction'].search([
            ('user_id', '=', self.id),
            ('ip_address', '=', client_ip),
        ])

        if existing:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Info',
                    'message': f'IP {client_ip} is already in your allowed list.',
                    'type': 'info',
                    'sticky': False,
                }
            }

        # Add new IP restriction
        self.env['user.ip.restriction'].create({
            'user_id': self.id,
            'ip_address': client_ip,
            'description': 'Added from current session',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Current IP {client_ip} has been added to allowed IPs.',
                'type': 'success',
                'sticky': False,
            }
        }
