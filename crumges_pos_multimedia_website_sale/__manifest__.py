{
    "name": "POS Multimedia - Website Sale Bridge",
    "version": "17.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "Unifica la multimedia del POS con las imágenes extra del eCommerce, evitando duplicados.",
    "author": "Crumges",
    "depends": ["crumges_pos_multimedia", "website_sale"],
    "data": [
        "views/product_template_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "crumges_pos_multimedia_website_sale/static/src/app/**/*",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "auto_install": True,
    "installable": True,
    "application": False,
    "license": "OPL-1",
}
