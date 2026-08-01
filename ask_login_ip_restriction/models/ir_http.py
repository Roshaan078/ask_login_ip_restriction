import logging
from werkzeug.exceptions import Forbidden
from odoo import models, http
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_client_ip(cls):
        """
        Extract client IP from request headers.
        Supports multiple proxy configurations.
        """
        request = http.request
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
    def _validate_ip_restriction(cls):
        """
        Validate IP restriction on every request.
        This is the second layer of security (request-level).
        """
        request = http.request
        if not request or not request.session.uid:
            return

        try:
            user = request.env['res.users'].browse(request.session.uid)

            # Only check if restriction is enabled
            if not user.enable_ip_restriction or not user.ip_restriction_ids:
                return

            # Get client IP
            client_ip = cls._get_client_ip()
            if not client_ip:
                _logger.warning(
                    f"Could not determine client IP for user {user.login} "
                    f"on request {request.httprequest.path}"
                )
                raise Forbidden(
                    "Your IP address could not be verified. "
                    "IP restriction is enabled but verification failed."
                )

            # Check IP restriction
            is_allowed, message = request.env['user.ip.restriction']._check_ip_restriction(
                user.id, client_ip
            )

            if not is_allowed:
                _logger.warning(
                    f"Unauthorized request from IP {client_ip} for user {user.login} "
                    f"on {request.httprequest.path}"
                )
                raise Forbidden(
                    f"Access denied. Your IP address ({client_ip}) is not authorized. "
                    "Contact your administrator."
                )

        except (AccessDenied, Forbidden):
            raise
        except Exception as e:
            _logger.error(f"Error validating IP restriction: {str(e)}", exc_info=True)
            # Don't block on errors - let user access
            pass

    @classmethod
    def _pre_dispatch(cls, rule, args):
        """Validate IP on every dispatched request (Odoo 18 hook).

        This is Layer 2 of the dual-layer security:
        - Layer 1: login blocking (res_users.authenticate)
        - Layer 2: every request (here), so a valid session cannot be reused
          from a disallowed IP.
        """
        super()._pre_dispatch(rule, args)
        cls._validate_ip_restriction()
