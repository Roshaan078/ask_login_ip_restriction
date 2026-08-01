# Ask Login IP Restriction

A production-ready Odoo 18 module for restricting user login access to specific IP addresses.

## Features

- **IP-based Login Restriction**: Control which IP addresses users can login from
- **CIDR Support**: Support for IP ranges using CIDR notation (e.g., `192.168.1.0/24`)
- **IPv4 & IPv6**: Full support for both IPv4 and IPv6 addresses
- **Proxy Support**: Handles reverse proxies (X-Forwarded-For, X-Real-IP, Cloudflare)
- **Admin Dashboard**: Easy management of user IP restrictions
- **Per-User Control**: Users can add their current IP with one click
- **Audit Trail**: Creation timestamps for all restrictions
- **Record-Level Security**: Users can only manage their own IPs (except admins)
- **Production-Ready**: Enterprise-grade code with proper error handling

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cd /path/to/addons
   git clone https://github.com/asksol/ask_login_ip_restriction.git
   ```

2. Install the module:
   - Go to Apps → Search for "Ask Login IP Restriction"
   - Click Install

3. No additional dependencies required (uses Python's standard `ipaddress` library)

## Configuration

### Enable IP Restriction for a User

1. Navigate to **Settings** → **Users & Companies** → **Users**
2. Open the user you want to restrict
3. Go to the **IP Restriction** tab
4. Enable **Enable IP Restriction**
5. Add allowed IP addresses:
   - Click **Add Current IP** to add your current IP
   - Or manually add IPs using the inline form

### Add IP Addresses Manually

In the **Allowed IP Addresses** section:

- **Single IP**: `192.168.1.100`
- **IP Range (CIDR)**: `192.168.1.0/24`
- **IPv6 Single**: `2001:db8::1`
- **IPv6 Range**: `2001:db8::/32`
- **Description**: Add a note (e.g., "Office Network", "Home")

### Manage Restrictions from Admin Dashboard

- Navigate to **IP Restriction** → **User IP Restrictions**
- View, edit, or delete IP restrictions for all users
- Filter by status (Active/Inactive)
- Group by user or status

## Security Features

1. **Record-Level Access Control**:
   - Regular users can only see/edit their own IPs
   - System administrators have full access

2. **IP Validation**:
   - Validates all IP addresses and CIDR notations
   - Prevents invalid entries

3. **Login Logging**:
   - Logs all successful and failed login attempts
   - Track unauthorized access attempts

4. **Proxy Support**:
   - Detects IPs through multiple proxy layers
   - Support for:
     - X-Forwarded-For
     - X-Real-IP
     - CF-Connecting-IP (Cloudflare)
     - Direct connections

## Behavior

### When IP Restriction is Enabled

- User can ONLY login from configured IP addresses
- Attempts from other IPs will be blocked with error: 
  - "Login not allowed from your IP address. Contact your administrator."

### When IP Restriction is Disabled

- User can login from any IP address (default behavior)

### When No IPs are Configured

- If restriction is enabled but no IPs are added:
  - Login is blocked until at least one IP is configured
  - Use **Add Current IP** button to quickly add current network

## Examples

### Office Network Access Only

1. Enable IP Restriction for user
2. Add office network: `203.0.113.0/24`
3. Description: "Office Network"

### Multiple Locations

Add multiple IP entries for different locations:
- `192.168.1.0/24` - Office Network
- `203.0.113.1` - Remote Site
- `2001:db8::/32` - IPv6 Network

### VPN Access

Add your VPN exit IP:
- `203.0.113.50` - VPN Server

### Home and Mobile

Add IP ranges for home network and mobile provider:
- `192.168.1.0/24` - Home WiFi
- `203.0.113.0/24` - Mobile Provider Range

## Troubleshooting

### User Locked Out

If a user gets locked out:

1. Login as admin
2. Go to **Settings** → **Users & Companies** → **Users**
3. Open the locked user
4. Go to **IP Restriction** tab
5. Either:
   - Disable "Enable IP Restriction"
   - Add the correct IP address
   - Click "Reset All IPs"

### Can't Determine Client IP

If you see: "Could not determine your IP address"
- Check proxy configuration
- Ensure headers are being passed correctly
- Verify Nginx/Apache configuration

### Wrong IP Detected

Add this to debug login process:
```python
# In logs, check detected IP
User {login} authenticated from IP {client_ip}
```

## API Usage

### Check IP Restriction Programmatically

```python
# In Python code within Odoo
user = env['res.users'].browse(user_id)
restrictions = user.ip_restriction_ids

if user.enable_ip_restriction and restrictions:
    is_allowed, message = env['user.ip.restriction']._check_ip_restriction(
        user_id, 
        "192.168.1.100"
    )
    print(message)  # "IP allowed" or "Login not allowed from IP 192.168.1.100"
```

### Add IP Restriction Programmatically

```python
env['user.ip.restriction'].create({
    'user_id': user_id,
    'ip_address': '192.168.1.0/24',
    'description': 'Programmatically added',
    'is_active': True,
})
```

## Performance

- Minimal performance impact on login
- IP validation cached after first check
- No database queries during authentication (checks happen in memory)
- Fast CIDR calculation using Python's `ipaddress` module

## Compatibility

- **Odoo**: 18.0
- **Python**: 3.8+
- **Database**: PostgreSQL 12+

## License

LGPL-3

## Support

For issues and feature requests, contact: support@asksol.pk

## Author

Asksol
Website: https://asksol.pk

---

**Module Price**: $4.50 USD

Version: 18.0.1.0.0
