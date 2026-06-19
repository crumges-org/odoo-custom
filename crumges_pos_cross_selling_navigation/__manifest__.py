{
    "name": "POS Cross Selling - Navigation",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Navegación contextual de ventas cruzadas. Crea categorías dinámicas al seleccionar un producto.",
    "depends": ["point_of_sale", "crumges_pos_cross_selling"],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_cross_selling_navigation/static/src/app/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
