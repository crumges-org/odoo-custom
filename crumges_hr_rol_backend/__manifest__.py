# -*- coding: utf-8 -*-
{
    'name': "Rol de Empleados en Backend",
    'summary': "Muestra el rol del empleado en la cabecera del backend",
    'author': "Antigravity",
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'depends': ['web', 'hr', 'crumges_hr_rol'],
    'assets': {
        'web.assets_backend': [
            'crumges_hr_rol_backend/static/src/systray_role/systray_role.js',
            'crumges_hr_rol_backend/static/src/systray_role/systray_role.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
