{
    'name': 'Project Task Sale Delivery Report',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Report task progress as delivered quantity and notes to Sales Orders.',
    'author': 'Crumges',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'sale_project',
        'sale_management',
    ],
    'data': [
        'views/product_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
}
