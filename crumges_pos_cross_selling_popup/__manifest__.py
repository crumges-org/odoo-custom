{
    "name": "POS Cross Selling - Auto Popup",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Muestra un popup forzado al añadir un producto con accesorios (UX Proactiva).",
    "depends": ["point_of_sale", "crumges_pos_cross_selling"],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_cross_selling_popup/static/src/app/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
