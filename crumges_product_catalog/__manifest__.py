{
    "name": "Crumges Product Catalog",
    "version": "18.0.1.0.0",
    "summary": "Catálogo de productos avanzado: PDF, email, membrete personalizado y grilla configurable",
    "category": "Inventory",
    "author": "Crumges",
    "license": "OPL-1",
    "depends": ["product", "mail", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/catalog_config_views.xml",
        "views/catalog_wizard_views.xml",
        "report/catalog_report_action.xml",
        "report/catalog_template.xml",
    ],
    "installable": True,
    "application": False,
}
