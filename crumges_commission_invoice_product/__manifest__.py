{
    "name": "Facturación Automática de Comisiones",
    "version": "18.0.1.0.0",
    "category": "Sales/Commissions",
    "summary": "Asigna automáticamente el producto al facturar liquidaciones de comisiones",
    "description": """
Facturación Automática de Comisiones
====================================

Este módulo simplifica la creación de facturas a partir de liquidaciones de comisiones.
Al momento de crear la factura de proveedor desde el asistente, no requiere que el usuario
seleccione manualmente un producto. El módulo crea un producto predeterminado (Comisiones por Pagar)
y lo preselecciona de forma invisible en el flujo de facturación.
    """,
    "author": "Crumges",
    "website": "https://crumges.com",
    "license": "LGPL-3",
    "depends": ["account_commission_oca"],
    "data": [
        "data/product_data.xml",
        "wizards/wizard_invoice_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
