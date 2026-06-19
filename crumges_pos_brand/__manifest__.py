# -*- coding: utf-8 -*-
{
    'name': "POS Product Brand",
    'summary': "Integrate product brands into Point of Sale",
    'description': """
        Adds brand logos, brand filtering, and brand search to the Point of Sale.
        Allows showing the brand name on the POS receipt and order lines.
    """,
    'author': "Antigravity",
    'category': 'Point of Sale',
    'version': '17.0.1.0.0',
    'depends': ['point_of_sale', 'product_brand'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_brand/static/src/app/store/pos_db.js',
            'crumges_pos_brand/static/src/app/store/pos_store.js',
            'crumges_pos_brand/static/src/app/store/models.js',
            'crumges_pos_brand/static/src/app/screens/product_screen/product_list/product_list.js',
            'crumges_pos_brand/static/src/app/screens/product_screen/product_list/product_list.xml',
            'crumges_pos_brand/static/src/app/generic_components/product_card/product_card.js',
            'crumges_pos_brand/static/src/app/generic_components/product_card/product_card.xml',
            'crumges_pos_brand/static/src/app/screens/product_screen/product_info_popup/product_info_popup.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
