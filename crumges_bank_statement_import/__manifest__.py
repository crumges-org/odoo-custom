{
    'name': 'Crumges Bank Statement Import (Excel)',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Importador de Extractos Bancarios desde Excel con configuraciones flexibles por Banco.',
    'description': """
Crumges Bank Statement Import
=============================

Permite importar extractos bancarios desde Excel de manera inteligente:
* Selector de formato por Banco para adaptarse a diferentes Excel.
* Detección de duplicados basada en Saldo e Importe para evitar cargar dos veces la misma línea.
* Panel de revisión previo a la importación.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
    ],
    'external_dependencies': {'python': ['openpyxl']},
    'data': [
        'security/ir.model.access.csv',
        'views/bank_statement_template_view.xml',
        'views/import_wizard_view.xml',
        'views/import_history_view.xml',
        'views/menu_items.xml',
        'data/demo_bank_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crumges_bank_statement_import/static/src/css/wizard_styles.css',
        ],
    },
    'installable': True,
    'application': False,
    'maintainers': ['Crumges'],
}
