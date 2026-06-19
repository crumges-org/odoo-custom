{
    "name": "Portal del Agente para Liquidaciones",
    "version": "18.0.1.0.0",
    "category": "Sales/Commissions",
    "summary": "Muestra las liquidaciones de comisiones en el portal web del agente",
    "description": """
Portal del Agente para Liquidaciones
====================================

Este módulo permite que los agentes accedan a su portal en Odoo para visualizar el estado
de sus liquidaciones de comisiones. Podrán ver la lista de liquidaciones, su estado, totales
y acceder al detalle para revisar las facturas o ventas asociadas a dicha liquidación.
    """,
    "author": "Crumges",
    "website": "https://crumges.com",
    "license": "LGPL-3",
    "depends": [
        "portal",
        "account_commission_oca",
        "mail",
        "crumges_commission_sequence",
    ],
    "data": [
        "security/commission_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "views/commission_settlement_views.xml",
        "views/portal_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
