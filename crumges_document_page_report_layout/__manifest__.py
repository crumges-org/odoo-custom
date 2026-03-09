{
    'name': 'Document Page Report Layout',
    'version': '18.0.1.0.0',
    'category': 'Knowledge',
    'summary': 'Configurable Report Layouts for Document Pages',
    'author': 'Crumges',
    'depends': ['base', 'web', 'document_page', 'crumges_report_layout_config'],
    'data': [
        'security/ir.model.access.csv',
        'views/document_page_views.xml',
        'views/document_page_print_template.xml',
        'wizards/document_page_report_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
