{
    'name': 'Report Layout Configuration (Generic)',
    'version': '18.0.1.0.0',
    'summary': 'Generic module to configure report layouts visually',
    'category': 'Productivity/Knowledge',
    'author': 'Crumges',
    'license': 'AGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/report_layout_data.xml',
        'views/report_layout_config_views.xml',
    ],
    'installable': True,
    'application': False,
}
