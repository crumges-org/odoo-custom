{
    'name': 'Confirmed Sale Order Price Update',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Recalculate prices in confirmed sale orders',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mass_recalculate_prices_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}