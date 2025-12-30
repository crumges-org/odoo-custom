# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Ticket Hierarchy - Tickets Relacionados',
    'version': '18.0.1.0.1',
    'category': 'Helpdesk Custom',
    'summary': 'Organice el caos: Agrupe múltiples incidencias bajo un caso maestro.',
    'description': """
Helpdesk Ticket Hierarchy
=========================

Organice el caos: Agrupe múltiples incidencias bajo un caso maestro.

Gestione casos de soporte complejos con facilidad mediante relaciones Padre/Hijo. A menudo, un problema reportado (Ticket Padre) desencadena múltiples subtareas o problemas relacionados (Tickets Hijos).

Funcionalidad
-------------
*   **Relación Padre/Hijo:** Navegue fácilmente entre tickets relacionados.
*   **Portal de Cliente:** Sus clientes ven la relación en su portal.
*   **Herencia de Contacto:** El hijo hereda el cliente del padre automáticamente.
""",
    'description': """
Helpdesk Ticket Hierarchy
=========================

Gestione casos de soporte complejos con facilidad mediante relaciones Padre/Hijo.

Funcionalidad
-------------
A menudo, un problema reportado (Ticket Padre) desencadena múltiples subtareas o problemas relacionados (Tickets Hijos).
Este módulo le permite:
*   Vincular tickets existentes como hijos o padres.
*   Navegar fácilmente entre tickets relacionados desde la vista de formulario.
*   Ver la estructura completa en una pestaña dedicada.
*   **Portal de Cliente**: Sus clientes también pueden ver la relación y navegar entre tickets en el portal.

Características Extra
---------------------
*   **Herencia de Contacto**: Al asignar un ticket padre, el ticket hijo hereda automáticamente el cliente del padre.

Requisitos
----------
Este módulo depende de **Odoo Helpdesk**, que es una aplicación **Enterprise**.
    """,
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'web', 
        'helpdesk'
    ],
    'data': [
        "views/helpdesk_ticket_views.xml",
        "views/tickets_followup_template.xml",
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'maintainers': ['Crumges'],
}
