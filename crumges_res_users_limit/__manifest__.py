{
    "name": "Límite de Usuarios",
    "version": "18.0.1.0.1",
    "summary": "Restringe la cantidad de usuarios internos activos en el sistema",
    "category": "Hidden/Tools",
    "author": "Crumges",
    "website": "https://crumges.com",
    "depends": ["base", "base_setup"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "crumges_res_users_limit/static/src/components/*",
            "crumges_res_users_limit/static/src/views/*",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
