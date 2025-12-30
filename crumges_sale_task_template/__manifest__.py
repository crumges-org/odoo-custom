# -*- coding: utf-8 -*-
{
    'name': 'Sale Task Template - Plantillas de Tareas desde Ventas',
    'version': '18.0.1.0.1',
    'category': 'Sales/Project',
    'summary': 'Estandarice sus servicios: Venda productos y genere estructuras de trabajo completas al instante.',
    'description': """
Sale Task Template
==================

Estandarice sus servicios: Venda productos y genere estructuras de trabajo completas al instante.

¿Vende servicios estandarizados que siempre requieren los mismos pasos? Este módulo permite definir una "Tarea Maestra" y clonarla automáticamente al confirmar una venta.

Solución
--------
Cuando venda un servicio, Odoo creará una tarea que es un **clon perfecto** de su plantilla, incluyendo:
*   Subtareas (y sus horas asignadas)
*   Etiquetas
*   Descripción detallada (checklist, instrucciones)
*   Prioridad y color
""",
    'description': """
Sale Task Template
==================

¿Vende servicios estandarizados que siempre requieren los mismos pasos?
Este módulo es la pieza que le falta a Odoo estándar.

Problema
--------
Odoo permite crear una tarea al vender un servicio, pero esa tarea viene vacía.
Tiene que crear manualmente las subtareas, asignar etiquetas y escribir las instrucciones una y otra vez.

Solución
--------
Defina una "Tarea Maestra" (Plantilla) y asóciela a su producto de servicio.
Cuando venda ese servicio, Odoo creará una tarea que es un **clon perfecto** de su plantilla, incluyendo:
*   Subtareas (y sus horas asignadas)
*   Etiquetas
*   Descripción detallada (checklist, instrucciones)
*   Prioridad y color

Ideal para agencias, consultoras y empresas de implementación.
    """,
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': [
        'sale_project',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'maintainers': ['Crumges'],
}