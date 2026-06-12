# -*- coding: utf-8 -*-
{
    'name': 'Crumges POS Epson Printer Protocol',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Fixes Epson printer protocol issues in POS',
    'description': "Allows specifying the http:// or https:// protocol explicitly in the Epson printer IP setting.",
    'depends': ['pos_epson_printer'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_config_views.xml',
        'views/pos_printer_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_epson_printer_protocol/static/src/app/epson_printer_patch.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
