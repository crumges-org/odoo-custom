# -*- coding: utf-8 -*-
{
    'name': 'Project Subtask Visible Default - Visibilidad Automática de Subtareas',
    'version': '18.0.1.0.3',
    'category': 'Project',
    'summary': 'Hace visibles las subtareas automáticamente en Proyectos. No más subtareas ocultas.',
    'description': """
Project Subtask Visible Default
===============================

¿Cansado de que Odoo oculte sus subtareas por defecto?
------------------------------------------------------

En Odoo estándar, cuando crea una subtarea, a menudo debe activarla manualmente para verla en las vistas de proyecto.
Este módulo resuelve ese problema automáticamente.

Características Principales
---------------------------
*   **Visibilidad Automática**: Las subtareas se crean con `display_in_project` = True por defecto.
*   **Sin Configuración**: Instalar y listo. Funciona en segundo plano.
*   **Compatibilidad**: Soporta múltiples campos de visibilidad usados por Odoo Enterprise y Community.
*   **Retroactividad**: También aplica la configuración por defecto al crear tareas desde la interfaz.

Ahorre clicks y evite la confusión de "¿dónde está mi subtarea?" con esta utilidad esencial.
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