# -*- coding: utf-8 -*-
{
    'name': 'Wapp-custom',
    'version': '18.0.0.1',
    'summary': """ Wapp-custom Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'whatsapp_connector'],
    "data": [
        "views/user_menu_views.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'wapp-custom/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
