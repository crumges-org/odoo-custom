{
    'name': 'Knowledge Report Layout (Specific)',
    'version': '18.0.1.0.0',
    'summary': 'Applies custom report layouts to Knowledge Articles',
    'category': 'Productivity/Knowledge',
    'author': 'Crumges',
    'license': 'AGPL-3',
    'depends': ['knowledge', 'crumges_report_layout_config'],
    'data': [
        'security/ir.model.access.csv',
        'views/knowledge_article_views.xml',
        'wizards/knowledge_report_wizard_views.xml',
        'report/knowledge_report_actions.xml',
        'report/knowledge_report_templates.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'crumges_knowledge_report_layout/static/src/components/knowledge_topbar/knowledge_topbar_patch.js',
            'crumges_knowledge_report_layout/static/src/components/knowledge_topbar/knowledge_topbar_patch.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
