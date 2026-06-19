{
    "name": "POS Cross Selling Website Bridge",
    "version": "17.0.1.0.0",
    "category": "Hidden",
    "summary": "Módulo puente para unificar la venta cruzada entre POS y eCommerce.",
    "description": """
        Este módulo se auto-instala cuando están presentes el POS (con cross-selling)
        y el módulo de eCommerce (website_sale). Unifica los campos para evitar la doble carga
        de información de productos relacionados/accesorios.
    """,
    "author": "Crumges",
    "depends": ["crumges_pos_cross_selling", "website_sale"],
    "data": [
        "views/product_template_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "auto_install": True,
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
