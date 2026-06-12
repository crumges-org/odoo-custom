# -*- coding: utf-8 -*-
{
    'name': "Rol de Empleados en POS",
    'summary': "Muestra el rol del empleado en la cabecera del Punto de Venta",
    'description': """
        Extiende el POS para cargar el rol del empleado y mostrarlo en la barra de navegación (Navbar) 
        junto al nombre del empleado.
    """,
    'author': "Antigravity",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ['point_of_sale', 'pos_hr', 'crumges_hr_rol'],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_hr_rol/static/src/app/navbar/navbar.xml',
            'crumges_pos_hr_rol/static/src/app/selection_popup.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
