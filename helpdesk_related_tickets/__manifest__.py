# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk relating tickets',
    'version': '18.0.0.1',
    'summary': """ Module for custom helpdesk functionality. For example relating tickets to each other. """,
    'author': 'Alain ALvarez Caignet <alain89042617783@gmail.com>',
    'website': '',
    'category': 'Helpdesk Custom',
    'depends': ['base', 'web', 'helpdesk'],
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/tickets_followup_template.xml",
    ],
    'assets': {
        'web.assets_backend': [
            # 'helpdesk-custom/static/src/**/*'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
