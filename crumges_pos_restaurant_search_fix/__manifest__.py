# -*- coding: utf-8 -*-
{
    'name': 'POS Restaurant Search Fix',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Fix search by table and floating order name in POS Restaurant.',
    'author': 'Crumges',
    'depends': ['point_of_sale', 'pos_restaurant'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_restaurant_search_fix/static/src/overrides/ticket_screen.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
