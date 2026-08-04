{
    'name': 'Ask Login IP Restriction',
    'version': '19.0.1.0.0',
    'category': 'Security',
    'author': 'Asksol',
    'website': 'https://asksol.pk',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 4.5,
    'currency': 'USD',
    'description': '''
        Professional IP-Based Access Control for Odoo
        
        🔒 DUAL-LAYER SECURITY
        ✅ Layer 1: Login-level blocking
        ✅ Layer 2: Request-level validation (every page, API, RPC)
        
        ✨ KEY FEATURES
        • Per-user IP whitelist with CIDR notation
        • IPv4 and IPv6 support
        • Proxy-aware IP detection (X-Forwarded-For, Cloudflare, Nginx)
        • Blocks at login AND on every request
        • Easy toggle enable/disable per user
        • Audit logging with detailed tracking
        • Record-level access control
        
        💰 COMPETITIVE ADVANTAGES
        ✅ 15% cheaper than alternatives ($4.50)
        ✅ CIDR range support (entire networks in one entry)
        ✅ Full IPv6 compatibility
        ✅ Dual-layer protection (login + request-level)
        ✅ 64+ pages of documentation
        ✅ Free lifetime updates
        
        🎯 PERFECT FOR
        • Securing remote team access
        • Multi-location businesses
        • VPN and proxy deployments
        • Enterprise deployments
        
        📚 INCLUDED
        • Quickstart guide (5-minute setup)
        • Technical documentation
        • Installation & deployment guides
        • Troubleshooting guide
        • Architecture documentation
    ''',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/res_users_views.xml',
        'views/user_ip_restriction_views.xml',
        'views/menu.xml',
    ],
    'external_dependencies': {
        'python': ['ipaddress'],
    },
}
