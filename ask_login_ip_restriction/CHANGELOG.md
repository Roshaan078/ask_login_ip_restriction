# Changelog

All notable changes to the Ask Login IP Restriction module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [18.0.1.0.0] - 2024-01-15

### Added
- Initial release for Odoo 18.0
- Core IP restriction functionality
  - Support for IPv4, IPv6, and CIDR notation
  - Per-user IP allowlisting
  - Admin dashboard for IP management
- Authentication interception and validation
- Proxy header support
  - X-Forwarded-For
  - X-Real-IP
  - CF-Connecting-IP (Cloudflare)
  - Direct remote_addr fallback
- User interface
  - IP Restriction tab in user form
  - Quick "Add Current IP" action
  - Detailed IP management views
  - Search and filtering capabilities
- Security features
  - Record-level access control
  - Model-level permissions
  - User can only manage their own IPs
  - System admins have full access
- Features
  - Enable/disable restriction per user
  - Active/inactive toggle for IPs
  - Description field for IP references
  - Creation timestamp for audit trail
  - Unique constraint on user-IP pairs
- Error handling
  - Validation error messages
  - Access denied with clear messaging
  - Comprehensive logging
- Documentation
  - README.md - User guide
  - TECHNICAL.md - Architecture documentation
  - INSTALLATION.md - Deployment guide
  - FILE_STRUCTURE.md - Component reference
  - CHANGELOG.md - Version history
- Testing infrastructure
  - Unit test scenarios documented
  - Integration test guidelines
  - Troubleshooting guide

### Technical Details
- Python: 3.8+ compatible
- Database: PostgreSQL 12+
- Dependencies: Python standard library only (ipaddress module)
- No external API calls required
- Performance optimized for login operations

### Known Limitations
- None known in initial release

### Future Roadmap

#### 18.0.2.0.0 (Planned)
- [ ] IP range editor UI improvements
- [ ] Bulk IP import functionality
- [ ] IP change notifications via email
- [ ] Geolocation display for IPs
- [ ] Session termination on IP change option
- [ ] Temporary IP exceptions (time-limited access)

#### 18.0.3.0.0 (Planned)
- [ ] Device fingerprinting integration
- [ ] Time-based access restrictions
- [ ] VPN detection
- [ ] IP whitelist/blacklist separation
- [ ] Integration with security dashboard
- [ ] Custom authentication failure reasons

#### Future (Backlog)
- [ ] Mobile app support
- [ ] API token IP restriction
- [ ] Two-factor authentication integration
- [ ] Okta/SAML provider IP checks
- [ ] AWS IAM integration
- [ ] Geographic location restrictions
- [ ] Risk-based adaptive authentication
- [ ] Integration with threat intelligence feeds

## Upgrade Instructions

### From 18.0.1.0.0 to Future Versions

```bash
# 1. Backup database
pg_dump -Fc odoo_db > backup_before_upgrade.dump

# 2. Update module code
git pull origin main
# OR
cp -r ask_login_ip_restriction /path/to/addons/

# 3. Restart Odoo
sudo systemctl restart odoo

# 4. Update module
# Settings > Apps > Ask Login IP Restriction > Upgrade

# 5. Verify
# Settings > IP Restriction > User IP Restrictions
# Test login from restricted IP
```

## Compatibility Matrix

| Odoo Version | Python | Status | Notes |
|--------------|--------|--------|-------|
| 18.0 | 3.8-3.11 | ✅ Supported | Production ready |
| 17.0 | 3.8-3.11 | ⚠️ Partial | Code adjustments needed |
| 16.0 | 3.8-3.10 | ❌ Not tested | Would require refactoring |
| 15.0+ | Any | ❌ Not supported | Requires Odoo 18 features |

## Browser Compatibility

All modern browsers supported:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Database Compatibility

- ✅ PostgreSQL 12+
- ✅ PostgreSQL 13
- ✅ PostgreSQL 14
- ✅ PostgreSQL 15

## Migration Guide

### From Other IP Restriction Modules

1. **Backup everything** ⚠️
   ```bash
   pg_dump -Fc odoo_db > backup.dump
   ```

2. **Note your restrictions** 📝
   - Export current IP restrictions if possible
   - Document setup for each user

3. **Uninstall old module** 🗑️
   ```
   Settings > Apps > [Old Module] > Uninstall
   ```

4. **Install this module** 📦
   ```
   Settings > Apps > Ask Login IP Restriction > Install
   ```

5. **Reconfigure restrictions** ⚙️
   - Re-add IP restrictions per user
   - Test login from restricted IPs

6. **Cleanup** 🧹
   - Remove old module files
   - Update documentation

## Support & Feedback

### Report Issues
- Email: support@asksol.pk
- Include: Odoo version, module version, error message, steps to reproduce

### Feature Requests
- Email: features@asksol.pk
- Subject: "[Feature Request] Your idea here"

### Security Issues
⚠️ **IMPORTANT**: Do NOT create public issues for security vulnerabilities
- Email privately: security@asksol.pk
- Include details and reproduction steps
- We'll handle responsibly and credit you

## Contributors

- **Asksol** - Initial development and maintenance

## License

LGPL-3 License - See LICENSE file for details

## Support & Maintenance

- **Active Development**: Yes
- **Maintenance**: Ongoing for Odoo 18.x
- **Security Updates**: High priority
- **Bug Fixes**: Regular
- **Feature Updates**: Quarterly

---

**Last Updated**: 2024
**Current Version**: 18.0.1.0.0
**Release Date**: 2024-01-15
**Status**: Stable & Production Ready

For version history prior to 18.0.1.0.0, check the git commit history.
