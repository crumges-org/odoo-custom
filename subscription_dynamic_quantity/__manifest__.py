# -*- coding: utf-8 -*-
{
    'name': 'Subscription Dynamic Quantity',
    'version': '18.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Automatically adjust subscription quantities based on service deliveries',
    'description': """
Subscription Dynamic Quantity Management
========================================

This module enables automatic quantity calculation for subscription products 
based on linked service deliveries (installations and uninstallations).

Key Features
------------
* Link installation/uninstallation products to subscription products
* Automatically add subscription lines when service products are added to sale orders
* Dynamic calculation of subscription quantities based on delivered services
* Real-time updates when deliveries are validated
* Prevention of negative quantities with automatic adjustment to 0

Use Case Example
----------------
A company offers GPS device installations with monthly subscriptions:
- Install 10 GPS devices → Subscription qty becomes 10
- Install 5 more devices → Subscription qty becomes 15
- Uninstall 2 devices → Subscription qty becomes 13

The module works with ANY service-subscription business model, not limited to GPS.

Technical
---------
* Compatible with Odoo 18 Community Edition
* No third-party dependencies
* Follows OCA development guidelines
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'sale_subscription',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
