{
    "name": "POS Cross Selling",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Agrega funcionalidad de venta cruzada (cross-selling) y productos accesorios al Punto de Venta de manera independiente.",
    "description": """
        Este módulo permite definir productos alternativos y accesorios en la ficha del producto
        para ser sugeridos en el Punto de Venta. No requiere el módulo de eCommerce (website_sale).
    """,
    "author": "Crumges",
    "depends": ["point_of_sale", "sale"],
    "data": [
        "views/product_template_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            # Aquí se añadirán los archivos JS y XML/OWL del frontend más adelante
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
