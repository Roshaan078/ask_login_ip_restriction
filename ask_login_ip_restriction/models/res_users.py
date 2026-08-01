import logging
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

    @classmethod
    def _get_request_ip(cls):
        """Extract client IP from the current request (proxy-aware)."""
        if not request:
            return None
        headers = request.httprequest.headers
        return (
            headers.get('CF-Connecting-IP')
            or (headers.get('X-Forwarded-For') or '').split(',')[0].strip()
            or headers.get('X-Real-IP')
            or request.httprequest.remote_addr
        )

    @classmethod
    def authenticate(cls, db, credential, user_agent_env=None):
        """Override authenticate (Odoo 18 signature) to block login by IP.

        In Odoo 17+ this is a classmethod and ``credential`` is a dict; the
        return value is the ``auth_info`` dict (with a ``uid`` key).
        """
        auth_info = super().authenticate(db, credential, user_agent_env)

        # Support both the modern dict result and a bare uid (older cores).
        uid = auth_info.get('uid') if isinstance(auth_info, dict) else auth_info
        if not uid:
            return auth_info

        with cls.pool.cursor() as cr:
            env = api.Environment(cr, uid, {})
            user = env['res.users'].browse(uid)

            if user.enable_ip_restriction and user.ip_restriction_ids:
                client_ip = cls._get_request_ip()

                if not client_ip:
                    _logger.warning("Could not determine client IP for user %s", user.login)
                    raise exceptions.AccessDenied(
                        "Could not determine your IP address. "
                        "IP restriction is enabled but verification failed."
                    )

                is_allowed, _msg = env['user.ip.restriction']._check_ip_restriction(uid, client_ip)
                if not is_allowed:
                    _logger.warning(
                        "Login attempt from unauthorized IP %s for user %s", client_ip, user.login
                    )
                    raise exceptions.AccessDenied(
                        f"Login not allowed from your IP address ({client_ip}). "
                        "Contact your administrator."
                    )

                _logger.info("User %s authenticated from IP %s", user.login, client_ip)

        return auth_info

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
