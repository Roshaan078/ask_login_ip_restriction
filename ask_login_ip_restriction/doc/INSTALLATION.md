# Installation & Deployment Guide

## Quick Start

### Prerequisites
- Odoo 18.0 installed
- Python 3.8+
- Database access
- System administrator privileges

### Installation Steps

#### 1. Copy Module to Addons Directory

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons

# Clone or copy the module
git clone https://github.com/asksol/ask_login_ip_restriction.git
# OR
cp -r ask_login_ip_restriction /path/to/odoo/addons/

# Fix permissions (if needed)
chown -R odoo:odoo ask_login_ip_restriction
chmod -R 755 ask_login_ip_restriction
```

#### 2. Install via Odoo UI

1. Restart Odoo service (optional but recommended)
   ```bash
   sudo systemctl restart odoo
   ```

2. Go to **Apps** menu
3. Click **Update Apps List** (top right)
4. Search for "Ask Login IP Restriction"
5. Click the module card
6. Click **Install** button
7. Wait for installation to complete

#### 3. Verify Installation

After installation:
- [ ] Module appears in installed apps list
- [ ] New "IP Restriction" menu visible under Settings
- [ ] Database has `user_ip_restriction` table created
- [ ] No errors in Odoo logs

## Configuration

### Step 1: Enable IP Restriction for Users

```bash
# Via UI (Recommended)
1. Settings > Users & Companies > Users
2. Select a user
3. Go to "IP Restriction" tab
4. Check "Enable IP Restriction"
5. Click "Add Current IP"
```

```bash
# Via Database (Quick admin setup)
psql -d odoo_db -c "
INSERT INTO res_users_rel (user_id, enable_ip_restriction) 
VALUES (2, true);
"
```

### Step 2: Configure Proxy Headers (if behind proxy)

If your Odoo is behind Nginx, Apache, or Cloudflare, ensure headers are passed:

**Nginx Configuration**:
```nginx
location / {
    proxy_pass http://odoo_backend;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Apache Configuration**:
```apache
ProxyPreserveHost On
ProxyPass / http://localhost:8069/
ProxyPassReverse / http://localhost:8069/
<IfModule mod_headers.c>
    RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s
    RequestHeader set X-Real-IP %{REMOTE_ADDR}s
</IfModule>
```

**Cloudflare**:
- Enable "Under Attack Mode" if needed
- Module automatically detects CF-Connecting-IP header

### Step 3: Test Configuration

1. Login as admin
2. Navigate to **IP Restriction > User IP Restrictions**
3. Verify table structure and data
4. Test login from restricted and non-restricted IPs

## Production Deployment

### 1. Pre-Deployment Checks

```bash
# Backup database
pg_dump -Fc odoo_db > odoo_db_backup_$(date +%Y%m%d).dump

# Check Odoo logs for errors
tail -f /var/log/odoo/odoo-server.log

# Verify module directory permissions
ls -la /path/to/odoo/addons/ask_login_ip_restriction/
```

### 2. Deployment Steps

```bash
# 1. Copy module (if not already done)
cp -r ask_login_ip_restriction /path/to/odoo/addons/

# 2. Update module list
# (From Odoo UI: Apps > Update Apps List)

# 3. Install module
# (From Odoo UI: Search and Install)

# 4. Create initial IP restrictions for admins
# (From UI: Settings > Users > IP Restriction tab)

# 5. Test login from restricted IPs
# (Should succeed from configured IPs)
```

### 3. Post-Deployment Verification

```bash
# Check database
psql -d odoo_db -c "SELECT COUNT(*) FROM user_ip_restriction;"

# Monitor logs
tail -n 100 /var/log/odoo/odoo-server.log | grep -i "ip"

# Test authentication
# Try login from restricted and non-restricted IPs
```

## Upgrade from Older Versions

### From Community Modules (Other IP Restriction)

If you're migrating from another IP restriction module:

```bash
# 1. Backup database
pg_dump -Fc odoo_db > backup_before_migration.dump

# 2. Uninstall old module
# Settings > Apps > [Old Module] > Uninstall

# 3. Install this module
# Settings > Apps > Ask Login IP Restriction > Install

# 4. Migrate data (if applicable)
# Manual recreation of restrictions recommended for safety

# 5. Verify
# Test login from restricted IPs
```

## Common Deployment Scenarios

### Scenario 1: Single Office Network

```
1. Enable IP Restriction for all users
2. Add office IP range (CIDR):
   - IP: 203.0.113.0/24
   - Description: "Main Office"
3. Users can login only from office
```

### Scenario 2: Multiple Locations

```
1. Enable for remote team members
2. Add each location:
   - 203.0.113.0/24 (Head Office)
   - 203.0.114.1 (Branch Office)
   - 203.0.115.50 (Customer Site)
3. Users can login from configured locations
```

### Scenario 3: Work From Home + Office

```
1. Enable IP Restriction
2. Add ranges:
   - 203.0.113.0/24 (Office)
   - Home ISP range (CIDR notation)
   - VPN server IP
3. Users flexible login options
```

### Scenario 4: Gradual Rollout

```
1. Install module (all users unrestricted)
2. Enable only for admin users first
3. Test thoroughly
4. Phase 2: Enable for team leads
5. Phase 3: Enable for all users
6. Gradual addition of IP restrictions
```

## Troubleshooting

### Issue: Module Not Appearing in Apps

**Solution**:
```bash
# 1. Restart Odoo
sudo systemctl restart odoo

# 2. Update apps list (UI)
Apps > Update Apps List

# 3. Check file permissions
chmod -R 755 /path/to/ask_login_ip_restriction/

# 4. Check Odoo logs
tail /var/log/odoo/odoo-server.log
```

### Issue: Login Blocked Unexpectedly

**Solution**:
```bash
# 1. As admin, check user settings
Settings > Users > [User] > IP Restriction tab

# 2. Verify IP is correct
# Add current IP or disable restriction temporarily

# 3. Check logs for errors
tail -f /var/log/odoo/odoo-server.log | grep -i "unauthorized"

# 4. Check proxy configuration
# Ensure X-Forwarded-For or X-Real-IP headers are passed
```

### Issue: Proxy IP Detected Incorrectly

**Solution**:
```bash
# 1. Check which header is detected
# Monitor logs during login attempt
tail -f /var/log/odoo/odoo-server.log

# 2. Configure correct proxy header in Nginx/Apache
# X-Forwarded-For (most common)
# X-Real-IP (alternative)
# CF-Connecting-IP (Cloudflare)

# 3. Add your IP using current IP detection
# UI: IP Restriction > Add Current IP button

# 4. Verify header passing
curl -i https://your-odoo.com -H "X-Forwarded-For: 192.168.1.100"
```

### Issue: Database Table Not Created

**Solution**:
```bash
# 1. Check if module installed correctly
# Settings > Apps > Search "Ask Login IP"
# Verify "Installed" status

# 2. Check database
psql -d odoo_db -c "\dt user_ip_restriction"

# 3. If table missing, uninstall and reinstall
# Apps > [Module] > Uninstall > Install

# 4. Check logs for SQL errors
grep -i "error\|table\|sql" /var/log/odoo/odoo-server.log
```

## Uninstallation

```bash
# 1. Via UI (Recommended)
Settings > Apps > Ask Login IP Restriction > Uninstall

# 2. Via Command Line
python /path/to/odoo/odoo-bin -d odoo_db -u ask_login_ip_restriction --uninstall

# 3. Remove module directory
rm -rf /path/to/odoo/addons/ask_login_ip_restriction

# 4. Backup will preserve data if needed later
```

## Support & Troubleshooting

### Getting Help

1. **Check Documentation**
   - README.md - User guide
   - TECHNICAL.md - Architecture details
   - This file - Installation guide

2. **Review Logs**
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   grep "ask_login_ip_restriction" /var/log/odoo/odoo-server.log
   ```

3. **Contact Support**
   - Email: support@asksol.pk
   - Website: https://asksol.pk

### Performance Monitoring

```bash
# Monitor login performance
# Add timing to logs (custom development)

# Check database query performance
psql -d odoo_db -c "
SELECT schemaname, tablename, idx_scan 
FROM pg_stat_user_indexes 
WHERE tablename LIKE '%ip_restriction%'
ORDER BY idx_scan DESC;
"
```

---

**Last Updated**: 2024
**Module Version**: 18.0.1.0.0
**Status**: Production Ready
