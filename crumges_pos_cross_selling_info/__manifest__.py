{
    "name": "POS Cross Selling - Info Tab",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Muestra los productos sugeridos en el popup de información del producto (UX Pasiva).",
    "depends": ["crumges_pos_cross_selling"],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_cross_selling_info/static/src/app/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
