# -*- coding: utf-8 -*-
{
    'name': 'Crumges POS Weighable Weight or Amount',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Permite ingresar peso o importe para productos pesables en el POS',
    'author': 'Antigravity',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_weighable_weight_or_amount/static/src/app/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
