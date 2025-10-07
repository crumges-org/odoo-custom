# -*- coding: utf-8 -*-
{
    'name': 'sale_extra_information',
    'version': '1.0.0',
    'summary': """ Sale Extra Information Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['extra_information', 'sale'],
    "data": [
        "views/sale_order_view.xml",
        "reports/sale_order_report.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'sale_extra_information/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
