{
    "name": "POS Multimedia",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Agrega soporte para imágenes adicionales y videos al visualizar la información del producto en el Punto de Venta.",
    "author": "Crumges",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_multimedia/static/src/app/**/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
