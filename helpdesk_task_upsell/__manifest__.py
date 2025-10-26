# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Ventas Adicionales en Suscripciones',
    'version': '18.0.1.0.0',
    'summary': """Gestión de ventas adicionales en suscripciones activas mediante la creación de tareas FSM desde tickets de helpdesk""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'category': 'Services/Helpdesk',
    'contributors': [
        'Crumges',
        'Alain Alvarez Caignet',
    ],
    'depends': ['helpdesk_fsm',
                'product',
                'sale_project',
                'sale_timesheet',
                'sale_subscription'],
    "data": [
        "data/product_data.xml",
        "security/ir.model.access.csv",
        # "views/helpdesk_ticket_views.xml",
        "views/upsell_category_views.xml",
        "wizards/create_task_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'helpdesk_task_upsell/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
