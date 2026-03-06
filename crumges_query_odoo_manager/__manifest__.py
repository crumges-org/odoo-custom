{
    'name': 'Query Odoo Manager',
    'summary': 'Execute and manage PostgreSQL queries with safety restrictions and Excel exports.',
    'description': """
        Manage SQL queries from the Odoo interface securely.
        Categorize queries, export to Excel, and enforce access rights.
    """,
    'author': 'Crumges',
    'category': 'Technical Settings',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/query_manager_views.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
