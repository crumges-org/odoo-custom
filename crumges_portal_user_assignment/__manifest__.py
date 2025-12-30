{
    'name': 'Portal User Assignment - Asignación de Usuarios de Portal',
    'summary': 'Extienda su fuerza laboral asignando tareas a usuarios de portal vinculados a empleados.',
    'description': """
Portal User Assignment
======================

Extienda su fuerza laboral: Integre contratistas y externos a su flujo de trabajo asignándoles tareas directamente, manteniendo la seguridad del acceso Portal.

Este módulo permite asignar tareas de proyectos a usuarios de tipo Portal, siempre y cuando estos usuarios tengan un registro de Empleado asociado.

Características Principales
---------------------------
*   **Asignación Flexible:** Permite seleccionar usuarios Portal en el campo "Asignado a" de las tareas.
*   **Seguridad Mantenida:** Los usuarios siguen siendo del tipo Portal, con permisos limitados.
*   **Integración con RRHH:** Vincula usuarios externos con registros de empleados para una gestión más completa.
""",
    'version': '18.0.1.0.0',
    'category': 'Project/Portal',
    'website': 'https://crumges.com',
    'author': 'Crumges',
    'maintainers': ['Crumges'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        "project",
        "hr",
    ],
    'data': [
        "views/project_task_views.xml",
    ],
    'images': ['static/description/icon.png'],
}
