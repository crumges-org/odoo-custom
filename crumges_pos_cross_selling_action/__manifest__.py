# -*- coding: utf-8 -*-
{
    'name': 'POS Cross Selling - Action Button',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Botón A Demanda para sugerencias de venta cruzada en el POS',
    'author': 'Antigravity',
    'depends': ['point_of_sale', 'crumges_pos_cross_selling'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_cross_selling_action/static/src/app/popups/cross_selling_popup.xml',
            'crumges_pos_cross_selling_action/static/src/app/popups/cross_selling_popup.js',
            'crumges_pos_cross_selling_action/static/src/app/control_buttons/cross_selling_button.xml',
            'crumges_pos_cross_selling_action/static/src/app/control_buttons/cross_selling_button.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
