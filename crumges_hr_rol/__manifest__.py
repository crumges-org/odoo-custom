# -*- coding: utf-8 -*-
{
    'name': "Roles de Empleados",
    'summary': "Módulo base para gestionar roles de empleados",
    'description': """
        Este módulo permite definir roles con sus respectivas notas y asignarlos a los empleados.
        Ejemplos: Cafetería, Panadería, Administración.
    """,
    'author': "Antigravity",
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'crumges_web_widget_emoji'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_employee_role_data.xml',
        'views/hr_employee_role_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
