# -*- coding: utf-8 -*-
{
    'name': 'Project Subtask Visible Default - Visibilidad Automática de Subtareas',
    'version': '18.0.1.0.3',
    'category': 'Project',
    'summary': 'Revele sus subtareas: Haga que el trabajo granular sea visible por defecto.',
    'description': """
Project Subtask Visible Default
===============================

Revele sus subtareas: Haga que el trabajo granular sea visible por defecto.

¿Cansado de que Odoo oculte sus subtareas? En Odoo estándar, las subtareas a menudo requieren activación manual para verse en las vistas principales. Este módulo automatiza ese proceso.

Características Principales
---------------------------
*   **Visibilidad Automática:** Las subtareas se crean visibles en Kanban y Lista por defecto.
*   **Cero Configuración:** Instalar y olvidar. Funciona automáticamente en segundo plano.
*   **Compatibilidad Total:** Soporta múltiples versiones y nombres de campos de visibilidad (Community/Enterprise).
*   **Retroactividad:** Aplica la configuración por defecto incluso al crear desde la interfaz rápida.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        # Sin vistas necesarias, lógica puramente Python
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'maintainers': ['Crumges'],
}