{
    "name": "Project Portal Full Chatter History",
    "summary": "¡Rompe las barreras de comunicación! Colaboración total para usuarios externos.",
    "version": "18.0.1.0.0",
    "category": "Project",
    "website": "https://www.crumges.com",
    "author": "Crumges",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
        "hr",
        "portal",
    ],
    "data": [
        # "security/ir.model.access.csv",
    ],
    "assets": {
    },
    "images": [
        "static/description/banner.png",
    ],
    "development_status": "Alpha",
    "maintainers": ["Crumges"],
    "description": """
¡Rompe las barreras de comunicación!
===================================

Permite que tus usuarios de portal (vinculados a empleados) visualicen todo el historial del chatter, notas y trazabilidad en sus proyectos para una colaboración sin límites.

Propósito
---------
Hacer que el usuario de portal, que tiene acceso a proyectos por invitación, pueda visibilizar las notas del chatter y los cambios de estados de los campos (tracking), obteniendo un historial completo.
Requiere que el usuario de portal tenga un empleado asignado para habilitar esta visión extendida.

Compatibilidad
--------------
- **Odoo Enterprise**: Compatible
- **Odoo Community**: Compatible
    """,
}
