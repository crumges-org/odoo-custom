{
    'name': 'CRM Subscription Upsell',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Create upsells for subscriptions from CRM Opportunities',
    'description': """
        This module adds a 'Subscriptions' tab to the CRM Opportunity form.
        It lists all active subscriptions for the customer and allows creating
        an upsell quotation directly from the list.
    """,
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'depends': ['crm', 'sale_management', 'sale_subscription'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'wizard/upsell_warning_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
