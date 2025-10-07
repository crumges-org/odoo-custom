# -*- coding: utf-8 -*-
{
    'name': 'Extra_information',
    'version': '18.0.1.0.0',
    'summary': """ Extra_information Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'partner_identification'],
    "data": [
        "security/ir.model.access.csv",
        "views/extra_information_category_views.xml",
        "views/extra_information_views.xml",
        "views/menu.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'extra_information/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
