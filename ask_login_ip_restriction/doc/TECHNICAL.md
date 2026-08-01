# Technical Documentation - Ask Login IP Restriction

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Login Request                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  ResUsers.authenticate()       │
        │  (Override)                    │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  Extract Client IP             │
        │  _get_client_ip()              │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  Check IP Restriction          │
        │  _check_ip_restriction()       │
        └────────────┬───────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌──────────┐         ┌──────────────┐
    │ Allowed  │         │  Blocked     │
    │ Login    │         │  AccessDenied│
    └──────────┘         └──────────────┘
```

## Module Structure

```
ask_login_ip_restriction/
├── __init__.py                 # Module initialization
├── __manifest__.py             # Module metadata & dependencies
├── README.md                   # User documentation
├── TECHNICAL.md               # This file
│
├── models/
│   ├── __init__.py
│   ├── user_ip_restriction.py  # IP restriction model
│   └── res_users.py            # ResUsers extension
│
├── views/
│   ├── __init__.py
│   ├── res_users_views.xml     # User form extension
│   ├── user_ip_restriction_views.xml  # CRUD views
│   └── menu.xml                # Menu definitions
│
└── security/
    ├── __init__.py
    ├── ir.model.access.csv     # Access control
    └── record_rules.xml        # Record-level rules
```

## Key Components

### 1. User IP Restriction Model (`models/user_ip_restriction.py`)

**Purpose**: Store and validate allowed IP addresses for users

**Key Methods**:

- `_validate_ip_address()` - Constrains method to validate IPv4, IPv6, and CIDR
- `is_ip_allowed(client_ip)` - Check if given IP matches allowed list
- `_check_ip_restriction(user_id, client_ip)` - Static method for login validation

**Data Model**:
```
user_id (M2O)         → res.users
ip_address (Char)     → IPv4/IPv6/CIDR
description (Char)    → Human-readable label
is_active (Boolean)   → Enable/disable restriction
created_date (DateTime) → Audit trail
```

**Validation**:
- Uses Python's `ipaddress` module for validation
- Supports CIDR notation: `ipaddress.ip_network()`
- Supports single IPs: `ipaddress.ip_address()`

### 2. ResUsers Extension (`models/res_users.py`)

**Purpose**: Intercept login and validate IP restrictions

**Override Methods**:

#### `authenticate(db, login, password, user_agent_env)`
- Calls parent `authenticate()` to get UID
- Checks if IP restriction is enabled for user
- Calls `_check_ip_restriction()` if enabled
- Raises `AccessDenied` exception if IP not allowed
- Logs successful authentication with IP

**Key Features**:
- Supports multiple proxy headers
- Falls back to direct remote_addr
- Comprehensive logging

#### `_get_client_ip()`
```
Priority order:
1. CF-Connecting-IP (Cloudflare)
2. X-Forwarded-For (Multiple proxies, takes first)
3. X-Real-IP (Nginx, Apache)
4. request.remote_addr (Direct connection)
```

**New Fields**:
```
enable_ip_restriction (Boolean) → Feature toggle
ip_restriction_ids (O2M)        → Related restrictions
```

**Action Methods**:

- `action_add_current_ip()` - Quick-add current IP
- `action_reset_ip_restrictions()` - Remove all IPs

### 3. UI Components

#### User Form Extension (`views/res_users_views.xml`)
- Adds **IP Restriction** tab to user form
- Conditional visibility based on `enable_ip_restriction`
- Quick action buttons
- Inline table editor
- Help text with examples

#### IP Restriction Views (`views/user_ip_restriction_views.xml`)
- **List View**: Quick inline editing
- **Form View**: Detailed configuration with examples
- **Search View**: Filter by user, status, and grouping
- **Action Window**: Menu item integration

## Data Flow Diagram

### Login Flow

```
User submits login form
         │
         ▼
   ResUsers.authenticate()
         │
         ├─ Parent authenticate() → Get UID
         │
         ├─ Is enable_ip_restriction = True?
         │  │
         │  ├─ No  → Allow login (return UID)
         │  │
         │  └─ Yes → Continue
         │     │
         │     ├─ _get_client_ip() → Extract IP
         │     │
         │     ├─ user.ip_restriction_ids exists?
         │     │  │
         │     │  ├─ No  → Allow login
         │     │  │
         │     │  └─ Yes → _check_ip_restriction()
         │     │     │
         │     │     ├─ is_ip_allowed() → Check CIDR
         │     │     │  │
         │     │     │  ├─ Match found → Allow (return UID)
         │     │     │  │
         │     │     │  └─ No match → Block (raise AccessDenied)
```

### Admin Management Flow

```
Admin opens user form
         │
         ▼
   Enable IP Restriction toggle
         │
         ├─ If Enabled → Show IP restrictions section
         │
         ├─ Add Current IP button
         │  └─ Creates new restriction with current IP
         │
         └─ Reset All IPs button
            └─ Delete all restrictions for user
```

## Security Implementation

### 1. Record-Level Access Control (`security/record_rules.xml`)

```xml
<!-- Regular Users -->
<rule domain="[('user_id', '=', user.id)]">
  Can read/write their own restrictions
  Cannot delete

<!-- System Admins -->
<rule domain="[(1, '=', 1)]">
  Full CRUD access
```

### 2. Model Access (`security/ir.model.access.csv`)

```
Regular Users:   Create, Read, Write (no Delete)
System Admins:   Create, Read, Write, Delete
```

### 3. Login Validation

- IP validation happens before session creation
- Invalid IPs trigger `AccessDenied` exception
- No sensitive data exposed in error messages
- Failed attempts are logged with IP address

## IP Validation Logic

```python
# Single IP check
client_ip = IPv4Address("192.168.1.100")
allowed_ip = IPv4Address("192.168.1.100")
client_ip == allowed_ip  # True

# CIDR range check
client_ip = IPv4Address("192.168.1.50")
network = IPv4Network("192.168.1.0/24", strict=False)
client_ip in network  # True

# IPv6 support
client_ip = IPv6Address("2001:db8::1")
network = IPv6Network("2001:db8::/32", strict=False)
client_ip in network  # True
```

## Performance Considerations

### Login Time Impact
- IP extraction: ~1ms (header lookup)
- IP validation: ~0.5ms (ipaddress module is optimized)
- Database query: ~10-50ms (search for user restrictions)
- **Total addition**: ~50-100ms per login (negligible)

### Caching Strategy
- No additional caching implemented (parent authenticate() already caches sessions)
- IP restrictions are queried once per login
- No memory bloat (restrictions cleaned up with user deletion)

### Database Indexes
- `user_id` indexed (M2O reference)
- `ip_address` indexed implicitly (part of unique constraint)
- Unique constraint: `(user_id, ip_address)` for data integrity

## Error Handling

### Login Exceptions
```python
# IP not allowed
raise exceptions.AccessDenied(
    f"Login not allowed from your IP address ({client_ip}). "
    "Contact your administrator."
)

# Cannot determine IP
raise exceptions.AccessDenied(
    "Could not determine your IP address. "
    "IP restriction is enabled but verification failed."
)

# Invalid IP format in restriction
raise exceptions.ValidationError(
    f"Invalid IP address or CIDR notation: {record.ip_address}"
)
```

### Logging
```
DEBUG:   User {login} authenticated from IP {client_ip}
WARNING: Login attempt from unauthorized IP {client_ip} for user {login}
WARNING: Could not determine client IP for user {login}
ERROR:   Error parsing IP restriction: {ip_address}
```

## Testing Scenarios

### Unit Tests to Implement

```python
# Test IP validation
def test_valid_ipv4()
def test_valid_ipv6()
def test_valid_cidr()
def test_invalid_ip_raises_error()

# Test IP matching
def test_exact_ip_match()
def test_cidr_range_match()
def test_ip_not_in_range()
def test_mixed_ipv4_ipv6()

# Test login flow
def test_login_allowed_matching_ip()
def test_login_blocked_non_matching_ip()
def test_login_allowed_when_disabled()
def test_login_allowed_when_no_restrictions()

# Test proxy headers
def test_cloudflare_ip_detection()
def test_nginx_x_real_ip()
def test_x_forwarded_for_first_ip()
def test_direct_remote_addr()
```

## Integration Points

### 1. With Odoo Core
- Extends `res.users` model
- Overrides `authenticate()` method
- Uses standard `AccessDenied` exception
- Integrates with user form UI

### 2. With External Systems
- No external API calls
- Uses standard HTTP headers (no vendor-specific setup needed)
- Works with any proxy/load balancer

### 3. Future Extensions
```python
# Possible enhancements:
- IP change notifications
- Temporary IP exceptions
- IP whitelist/blacklist
- Geolocation-based restrictions
- Device fingerprinting
- Time-based restrictions
- Session termination on IP change
```

## Deployment Checklist

- [ ] Module copied to addons path
- [ ] Module installed via Apps menu
- [ ] No conflicts with other IP restriction modules
- [ ] Proxy headers correctly configured
- [ ] User restrictions configured for admins
- [ ] Logging configured for audit trail
- [ ] Backup taken before enabling restrictions
- [ ] Test login from restricted IP (should succeed)
- [ ] Test login from non-restricted IP (should fail)
- [ ] Verify error messages in UI

## Maintenance

### Regular Tasks
1. Review authentication logs for suspicious activity
2. Audit user IP restrictions quarterly
3. Remove inactive users' restrictions
4. Update proxy configuration if infrastructure changes

### Troubleshooting Commands

```bash
# Check Odoo logs for auth attempts
tail -f /var/log/odoo/odoo-server.log | grep "Login attempt"

# Find all active restrictions
psql -d odoo_db -c "SELECT user_id, ip_address FROM user_ip_restriction WHERE is_active=True;"

# Disable restrictions for user (emergency access)
psql -d odoo_db -c "UPDATE res_users SET enable_ip_restriction=False WHERE login='user@example.com';"
```

---

**Last Updated**: 2024
**Module Version**: 18.0.1.0.0
