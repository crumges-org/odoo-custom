{
    'name': 'Gestión de Partes de Horas en Portal',
    'summary': 'Gestión de horas sin barreras: Permita que sus externos registren su trabajo directamente.',
    'description': """
Portal Timesheet Management
===========================

Gestión de horas sin barreras: Permita que sus externos registren su trabajo directamente.

Este módulo habilita una interfaz simplificada y potente en el portal para que contratistas y empleados externos puedan registrar, consultar y gestionar sus partes de horas (timesheets) de forma autónoma.

Características Principales
---------------------------
*   **Registro Rápido:** Formulario optimizado para carga ágil de horas.
*   **Selección Dinámica:** Filtrado inteligente de Tareas basado en el Proyecto seleccionado.
*   **Gestión Autónoma:** Permite a los usuarios borrar sus propios registros (si está configurado).
*   **Integración Transparente:** Se integra con el flujo nativo de Proyectos y Hojas de Horas.
""",
    'version': '18.0.1.0.12',
    'category': 'Services/Timesheets',
    'website': 'https://crumges.com',
    'author': 'Crumges',
    'maintainers': ['Crumges'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        "portal",
        "hr_timesheet",
        "project",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/hr_employee_views.xml",
        "views/res_users_views.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'crumges_portal_timesheet/static/src/js/timesheet_portal.js',
        ],
    },
    'images': ['static/description/icon.png'],
}
