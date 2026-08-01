# File Structure & Module Components

## Complete Directory Tree

```
ask_login_ip_restriction/
│
├── __init__.py                          # Module initialization (imports models)
├── __manifest__.py                      # Module metadata & configuration
│
├── README.md                            # User documentation
├── CHANGELOG.md                         # Version history
│
├── models/                              # Business logic layer
│   ├── __init__.py                      # Models package init
│   ├── user_ip_restriction.py           # IP restriction model (core logic)
│   ├── res_users.py                     # ResUsers extension (login intercept)
│   └── ir_http.py                       # Request-level IP validation
│
├── views/                               # User interface layer (XML data)
│   ├── res_users_views.xml              # User form extension
│   ├── user_ip_restriction_views.xml    # CRUD views & actions
│   └── menu.xml                         # Menu definitions
│
├── security/                            # Access control layer (CSV/XML data)
│   ├── ir.model.access.csv              # Model-level access control
│   └── record_rules.xml                 # Record-level access rules
│
├── static/
│   └── description/                     # Odoo Apps store assets (auto-detected)
│       ├── index.html                   # App listing page
│       └── icon.png                     # Module icon
│
└── doc/                                 # Extended documentation
    ├── TECHNICAL.md                     # Architecture & development guide
    ├── INSTALLATION.md                  # Installation & deployment guide
    ├── QUICKSTART.md                    # 5-minute setup guide
    ├── FILE_STRUCTURE.md                # This file
    ├── PACKAGE_INFO.md                  # Packaging notes
    └── DELIVERY_SUMMARY.md              # Delivery summary
```

> **Note:** `views/` and `security/` are data folders loaded via the manifest,
> so they do **not** contain `__init__.py`. Only `models/` is a Python package.

## File Descriptions

### Core Configuration Files

#### `__manifest__.py` (118 lines)
**Purpose**: Module metadata and configuration
- Module name, version, category
- Dependencies declaration
- Data files to load
- External dependencies (ipaddress)
- Module pricing

#### `__init__.py` (2 lines)
**Purpose**: Python package initialization
- Imports models package

### Documentation Files

#### `README.md` (350+ lines)
**Purpose**: End-user documentation
- Features overview
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting guide
- API usage examples

#### `TECHNICAL.md` (400+ lines)
**Purpose**: Technical architecture documentation
- Architecture diagrams (ASCII)
- Component descriptions
- Data flow diagrams
- Security implementation details
- IP validation logic
- Performance considerations
- Testing scenarios
- Integration points

#### `INSTALLATION.md` (300+ lines)
**Purpose**: Deployment and installation guide
- Prerequisites
- Step-by-step installation
- Configuration instructions
- Production deployment checklist
- Common scenarios
- Troubleshooting procedures

### Models (Business Logic)

#### `models/__init__.py` (2 lines)
**Purpose**: Models package initialization
- Imports user_ip_restriction module
- Imports res_users module

#### `models/user_ip_restriction.py` (130 lines)
**Purpose**: Core IP restriction model
- Model definition: `user.ip.restriction`
- Fields:
  - `user_id` (M2O): Related user
  - `ip_address` (Char): IPv4/IPv6/CIDR
  - `description` (Char): Label for user reference
  - `is_active` (Boolean): Enable/disable flag
  - `created_date` (DateTime): Audit trail
- Methods:
  - `_validate_ip_address()`: Constraint validation
  - `is_ip_allowed()`: IP matching logic
  - `_check_ip_restriction()`: Login validation
- Constraints:
  - Unique constraint on (user_id, ip_address)
  - IP format validation

#### `models/res_users.py` (180 lines)
**Purpose**: Odoo user model extension for IP restriction
- Extended fields:
  - `enable_ip_restriction` (Boolean): Feature toggle
  - `ip_restriction_ids` (O2M): Related IP restrictions
- Overridden methods:
  - `authenticate()`: Login interception & validation
  - `check_credentials()`: Credential validation
- Helper methods:
  - `_get_client_ip()`: Client IP extraction from headers
- Action methods:
  - `action_add_current_ip()`: Quick-add current IP
  - `action_reset_ip_restrictions()`: Clear all IPs

### Views (User Interface)

#### `views/__init__.py` (0 lines)
**Purpose**: Views package initialization

#### `views/res_users_views.xml` (60 lines)
**Purpose**: User form extension
- Extends `base.view_users_form`
- Adds "IP Restriction" tab
- Fields displayed:
  - Enable/disable toggle
  - Action buttons (Add IP, Reset IPs)
  - IP restriction inline table
  - Help text with examples
- Conditions:
  - Tab only visible when feature enabled
  - Action buttons conditional visibility

#### `views/user_ip_restriction_views.xml` (90 lines)
**Purpose**: IP restriction CRUD interface
- List view (`view_user_ip_restriction_tree`)
  - Inline editing enabled
  - Shows all fields
  - Inline add/edit/delete
- Form view (`view_user_ip_restriction_form`)
  - Detailed field layout
  - CIDR notation examples
  - Help text with IPv4/IPv6 examples
  - Status badge
- Search view (`view_user_ip_restriction_search`)
  - Filter by active/inactive
  - Group by user or status
- Action window
  - Menu item configuration
  - Help message

#### `views/menu.xml` (25 lines)
**Purpose**: Menu navigation
- Main menu: "IP Restriction"
- Submenu: "User IP Restrictions"
- Settings integration: Added under Administration

### Security (Access Control)

#### `security/__init__.py` (0 lines)
**Purpose**: Security package initialization

#### `security/ir.model.access.csv` (3 lines)
**Purpose**: Model-level access control
```csv
id,name,model_id:id,group_id:id,perm_create,perm_read,perm_write,perm_unlink
access_user_ip_restriction_user,user_ip_restriction_user,model_user_ip_restriction,base.group_user,1,1,1,0
access_user_ip_restriction_admin,user_ip_restriction_admin,model_user_ip_restriction,base.group_system,1,1,1,1
```
- Regular users: Create, Read, Write (no Delete)
- System admins: Full CRUD access

#### `security/record_rules.xml` (35 lines)
**Purpose**: Record-level access control
- User rule: Can only see/edit own restrictions
- Admin rule: Full access to all restrictions
- Prevents users from viewing other users' IPs

## File Statistics

| Component | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| Configuration | 1 | 50 | Module metadata |
| Models | 3 | 350+ | Business logic |
| Views | 4 | 200+ | User interface |
| Security | 3 | 50 | Access control |
| Documentation | 4 | 1000+ | Guides & docs |
| **Total** | **18** | **1700+** | **Production module** |

## Dependencies

### Python Standard Library
- `ipaddress` - IP address validation & CIDR parsing

### Odoo Core Modules
- `base` - User model, access control
- `web` - Web interface

### External Dependencies
- None (uses only Python standard library)

## Data Models

### Database Tables

#### `user_ip_restriction`
```sql
CREATE TABLE user_ip_restriction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES res_users(id) ON DELETE CASCADE,
    ip_address VARCHAR NOT NULL,
    description VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT NOW(),
    UNIQUE(user_id, ip_address)
);

CREATE INDEX idx_user_ip_user_id ON user_ip_restriction(user_id);
CREATE INDEX idx_user_ip_address ON user_ip_restriction(ip_address);
```

#### `res_users` (extended)
```sql
ALTER TABLE res_users ADD COLUMN enable_ip_restriction BOOLEAN DEFAULT FALSE;
-- One2many relationship through user_ip_restriction.user_id
```

## Loading Order

Odoo loads files in this sequence:

1. **Manifest** (`__manifest__.py`)
   - Defines dependencies and data files

2. **Python Models** (models/)
   - Define database schema
   - Create tables and fields

3. **Security** (security/)
   - Apply access control rules
   - Set record-level permissions

4. **Views** (views/)
   - Create UI elements
   - Add menus and actions

## Extensibility Points

### For Developers

The following can be extended without modifying core files:

1. **Add custom validation**
   ```python
   # Extend UserIPRestriction._validate_ip_address()
   ```

2. **Add custom IP sources**
   ```python
   # Extend ResUsers._get_client_ip()
   ```

3. **Add custom UI views**
   ```xml
   <!-- Inherit from existing views -->
   ```

4. **Add notification on login**
   ```python
   # Hook into authenticate() method
   ```

## Deployment Package

### What to Include in Distribution

```
ask_login_ip_restriction/
├── All files above (18 total)
├── .gitignore
├── LICENSE (LGPL-3)
├── CHANGELOG.md (version history)
└── .github/
    └── workflows/
        └── tests.yml (CI/CD configuration)
```

### What NOT to Include

- `.pyc` files
- `__pycache__` directories
- `.idea` or IDE-specific files
- `.env` or environment files
- Test data or fixtures
- Development branches

## Package Verification

Before distributing, verify:

- [ ] All 18 files present
- [ ] No `.pyc` or cache files
- [ ] Correct permissions (755 for dirs, 644 for files)
- [ ] Manifest syntax valid (Python)
- [ ] XML files well-formed
- [ ] CSV files properly formatted
- [ ] Documentation complete and accurate
- [ ] No hardcoded paths or credentials
- [ ] Version consistent across files

---

**Last Updated**: 2024
**Module Version**: 18.0.1.0.0
