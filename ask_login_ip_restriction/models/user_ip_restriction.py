import ipaddress
import logging
from odoo import models, fields, api, exceptions

_logger = logging.getLogger(__name__)


class UserIPRestriction(models.Model):
    _name = 'user.ip.restriction'
    _description = 'User IP Restriction'
    _table = 'user_ip_restriction'
    _order = 'create_date DESC'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    ip_address = fields.Char(
        string='IP Address / CIDR',
        required=True,
        help='IPv4, IPv6 or CIDR notation (e.g., 192.168.1.0/24)',
    )
    description = fields.Char(
        string='Description',
        help='E.g., Office Network, Home Network',
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )
    created_date = fields.Datetime(
        string='Created Date',
        readonly=True,
        default=fields.Datetime.now,
    )

    _unique_user_ip = models.Constraint(
        'UNIQUE(user_id, ip_address)',
        'IP address must be unique per user',
    )

    @api.constrains('ip_address')
    def _validate_ip_address(self):
        """Validate IP address or CIDR notation"""
        for record in self:
            try:
                ipaddress.ip_address(record.ip_address)
            except ValueError:
                try:
                    ipaddress.ip_network(record.ip_address, strict=False)
                except ValueError:
                    raise exceptions.ValidationError(
                        f"Invalid IP address or CIDR notation: {record.ip_address}"
                    )

    def is_ip_allowed(self, client_ip):
        """Check if given IP is allowed"""
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
        except ValueError:
            _logger.warning(f"Invalid client IP format: {client_ip}")
            return False

        for record in self:
            if not record.is_active:
                continue

            try:
                # Try to parse as network (CIDR)
                network = ipaddress.ip_network(
                    record.ip_address,
                    strict=False
                )
                if client_ip_obj in network:
                    return True
            except ValueError:
                # Try to parse as single IP
                try:
                    allowed_ip = ipaddress.ip_address(record.ip_address)
                    if client_ip_obj == allowed_ip:
                        return True
                except ValueError:
                    _logger.error(
                        f"Error parsing IP restriction: {record.ip_address}"
                    )

        return False

    @api.model
    def _check_ip_restriction(self, user_id, client_ip):
        """
        Check if user can login from given IP.
        Returns: (is_allowed, message)
        """
        restrictions = self.search([
            ('user_id', '=', user_id),
            ('is_active', '=', True),
        ])

        # If no restrictions, allow login
        if not restrictions:
            return True, "No IP restrictions"

        # Check if IP is allowed
        if restrictions.is_ip_allowed(client_ip):
            return True, "IP allowed"

        return False, f"Login not allowed from IP {client_ip}"
