# -*- coding: utf-8 -*-
{
    'name': 'stock_picking_extra_information',
    'version': '1.0.0',
    'summary': """ Stock_picking_extra_information Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['sale_stock', 'sale_extra_information'],
    'data': [
        "views/stock_picking_view.xml",
        "reports/stock_picking_report.xml"
    ],
    'assets': {
              'web.assets_backend': [
                  'stock_picking_extra_information/static/src/**/*'
              ],
          },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
