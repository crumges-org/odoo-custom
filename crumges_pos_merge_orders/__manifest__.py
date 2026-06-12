{
    "name": "POS Merge Orders",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Permite fusionar pedidos desde la pantalla de tickets del Punto de Venta",
    "author": "Crumges",
    "website": "https://www.crumges.com",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_merge_orders/static/src/overrides/ticket_screen/ticket_screen.xml",
            "crumges_pos_merge_orders/static/src/overrides/ticket_screen/ticket_screen.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
