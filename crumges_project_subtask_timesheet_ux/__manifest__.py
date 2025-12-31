{
    'name': 'UX de Subtareas y Partes de Horas',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Automatización inteligente: Deje que sus tareas se gestionen solas basado en el progreso real.',
    'description': """
Advanced Subtask & Timesheet UX
===============================

Automatización inteligente: Deje que sus tareas se gestionen solas basado en el progreso real.

La gestión manual de estados en proyectos complejos es propensa a errores. Este módulo automatiza el flujo: calcula estados de tareas padre basándose en el consumo de horas de sus subtareas, valida acciones críticas y permite autocompletar timesheets.

Características Principales
---------------------------
*   **Estados Automáticos:** Actualización dinámica del estado (Prioridad a Desvíos) y propagación en cascada.
*   **Auto-Timesheet & Auto-asignación:** Generación inteligente de líneas de tiempo al cerrar tareas.
*   **Acciones en Cascada:** Cancelación y Reapertura automática de subtareas desde la barra de estado.
*   **Validación:** Prevención de errores lógicos y de integridad de datos.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'AGPL-3',
    'maintainers': ['Crumges'],
    'depends': ['project', 'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/views/project_task_cancel_wizard_views.xml',
        'wizards/views/project_task_reopen_wizard_views.xml',
        'wizards/views/project_task_complete_wizard_views.xml',
        'views/project_task_views.xml',
        'views/project_sharing_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}