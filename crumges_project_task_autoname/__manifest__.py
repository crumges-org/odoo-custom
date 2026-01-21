{
    'name': 'Renombrado Automático de Tareas',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Nombres de tareas automáticos y estandarizados (Propósito + Info).',
    'description': """
        Este módulo automatiza la creación de nombres de tareas para asegurar limpieza y estandarización.
        
        Funcionalidades principales:
        - Nombres compuestos: [ID] - Propósito - Información Adicional.
        - Gestión de "Propósitos" de tarea configurables.
        - Bloqueo/Congelado del nombre una vez generado para evitar ediciones accidentales.
        - Ideal para talleres, servicios técnicos o flujos donde el ID único es vital.
    """,
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/task_purpose_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
