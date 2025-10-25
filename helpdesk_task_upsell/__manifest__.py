# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk_task_upsell',
    'version': '18.0.1.0.0',
    'summary': """ Helpdesk_task_upsell Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['helpdesk_fsm',
                'product',
                'sale_project',
                'sale_timesheet',
                'sale_subscription'],
    "data": [
        "data/product_data.xml",
        "views/helpdesk_ticket_views.xml",
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
