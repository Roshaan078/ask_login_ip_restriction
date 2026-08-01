# Quick Start Checklist

Get your IP restriction module up and running in 5 minutes.

## Pre-Installation (2 min)

- [ ] Odoo 18.0 installed and running
- [ ] Admin access to Odoo
- [ ] Database backup taken
- [ ] You know your current IP address (or use button to detect)

**How to find your IP**:
```bash
# Linux/Mac
curl ifconfig.me

# Windows
ipconfig
# Look for IPv4 Address under your network adapter
```

## Installation (2 min)

### Step 1: Copy Module
```bash
cd /path/to/odoo/addons
git clone https://github.com/asksol/ask_login_ip_restriction.git
# OR
cp -r ask_login_ip_restriction /path/to/odoo/addons/
```

### Step 2: Restart Odoo
```bash
sudo systemctl restart odoo
# Wait 10-15 seconds for restart
```

### Step 3: Install in UI

1. Go to **Apps** in Odoo
2. Click **Update Apps List** (top right, if first time)
3. Search: `Ask Login IP Restriction`
4. Click the result
5. Click **Install**
6. Wait for green checkmark

**✅ Module is now installed!**

---

## Initial Setup (1 min)

### For Admin User

1. Go to **Settings** → **Users & Companies** → **Users**
2. Click on your admin user
3. Scroll to **IP Restriction** tab
4. Toggle **Enable IP Restriction** → ON
5. Click **Add Current IP** button
6. Description: `"Admin PC"` (or your preference)
7. Click **Save**

**✅ Admin is now protected!**

### For Other Users (Repeat per user)

1. Select a user
2. Open **IP Restriction** tab
3. Enable toggle
4. Click **Add Current IP** (user must do from their PC)
5. Or manually add IP: `203.0.113.1`
6. Set description: `"Office Network"`
7. Save

**✅ User is protected!**

---

## Testing (Quick Verification)

### Test 1: Login from Allowed IP ✅ Should Succeed
```
1. Logout from Odoo
2. Login from configured IP
3. Should login successfully
```

### Test 2: Login from Blocked IP ❌ Should Fail
```
1. Use VPN or different network
2. Try to login
3. Should see: "Login not allowed from your IP address"
```

### Test 3: Admin Override
```
1. Login as admin
2. Go to Settings > Users
3. Select restricted user
4. Disable "Enable IP Restriction"
5. Now user can login from any IP
6. Re-enable when ready
```

---

## Common Tasks

### Add Another IP for a User
```
1. Settings > Users > Select User
2. IP Restriction tab
3. Click "Add a Line" in table
4. Enter: 192.168.2.100
5. Description: "Home WiFi"
6. Mark Active: ✓
7. Save
```

### Add CIDR Range (Multiple IPs)
```
Example: Entire office network
IP Address: 203.0.113.0/24
Description: "Office Building A"

This allows anyone in 203.0.113.1 to .254 to login
```

### Remove All Restrictions (Emergency)
```
1. Settings > Users > Select User
2. IP Restriction tab
3. Click "Reset All IPs" button
4. Confirm
5. All restrictions deleted
6. User can login from anywhere
```

### View All IP Restrictions (Admin)
```
1. Go to Settings > IP Restriction (bottom of left menu)
2. See all users' IP restrictions
3. Edit, disable, or delete as needed
4. Filter by Active/Inactive
```

---

## Troubleshooting Quick Reference

### Issue: "Login not allowed from IP"

**Solution**:
1. User asks admin to add their current IP
2. OR admin adds IP: User's IP → Add to restriction
3. User retries login

### Issue: Admin Locked Out

**Solution**:
```bash
# Database emergency access
psql -d odoo_db -c "UPDATE res_users SET enable_ip_restriction=FALSE WHERE login='admin';"

# Then in Odoo UI:
1. Login as admin
2. Settings > Users > Admin
3. Re-enable restriction
4. Add correct IPs
```

### Issue: "Could not determine your IP"

**Solution**:
1. Check if behind proxy
2. Ensure proxy headers pass through:
   - X-Forwarded-For, X-Real-IP, CF-Connecting-IP
3. Or add IP manually instead of "Add Current IP"

### Issue: VPN Users Blocked

**Solution**:
1. Get VPN server IP (static)
2. Add to user's restrictions
3. User can now login via VPN

### Issue: Mobile Users Can't Login

**Solution**:
1. Add ISP's IP range (CIDR)
2. Example: `203.0.113.0/16` (wide range)
3. Users on that ISP can login

---

## Best Practices

### ✅ DO

- ✅ Backup database before enabling
- ✅ Test from restricted IP first
- ✅ Add multiple IPs per user (office + home)
- ✅ Use CIDR for IP ranges
- ✅ Use clear descriptions
- ✅ Keep admin backup PC enabled
- ✅ Review logs monthly
- ✅ Document IP changes

### ❌ DON'T

- ❌ Don't enable without testing
- ❌ Don't forget backup IP for admins
- ❌ Don't use overly wide IP ranges (security risk)
- ❌ Don't change restrictions without notifying users
- ❌ Don't assume IP is permanent (may change)
- ❌ Don't block all users without emergency plan

---

## IP Address Examples

### Single IP (Exact Match)
```
192.168.1.100
User can login only from this exact IP
```

### Small Office (CIDR /24)
```
203.0.113.0/24
Allows: 203.0.113.1 to 203.0.113.254
```

### Large Network (CIDR /16)
```
203.0.0.0/16
Allows: 203.0.0.1 to 203.0.255.254
```

### IPv6 Single
```
2001:db8::1
Exact IPv6 address match
```

### IPv6 Range
```
2001:db8::/32
Large IPv6 network range
```

---

## Multi-Location Setup

### Example: Company with 3 Offices

**Office A**: 203.0.113.0/24
**Office B**: 203.0.114.1
**Home/Remote**: 203.0.115.0/24

Add all three IPs to each user:
```
User: john@company.com

IP 1: 203.0.113.0/24   (Office A)
IP 2: 203.0.114.1      (Office B)
IP 3: 203.0.115.0/24   (Remote)

John can login from any of these locations
```

---

## Support

- **Documentation**: Check README.md
- **Installation Help**: INSTALLATION.md
- **Technical Details**: TECHNICAL.md
- **Email**: support@asksol.pk
- **Website**: https://asksol.pk

---

## Next Steps

1. ✅ Install module
2. ✅ Test with admin
3. ✅ Configure users one by one
4. ✅ Test blocked IPs
5. ✅ Document setup
6. ✅ Train users on IP changes
7. ✅ Monitor logs monthly

**You're done! 🎉**

---

**Version**: 18.0.1.0.0
**Module**: Ask Login IP Restriction
**Time to Setup**: 5-10 minutes
**Difficulty**: Easy ⭐
