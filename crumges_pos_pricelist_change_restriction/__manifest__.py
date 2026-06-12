# -*- coding: utf-8 -*-
{
    'name': 'Crumges POS Pricelist Change Restriction',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Restringe o advierte sobre el cambio de lista de precios en el POS si el carrito tiene productos.',
    'author': 'Antigravity',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_pricelist_change_restriction/static/src/app/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
