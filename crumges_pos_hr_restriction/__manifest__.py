# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
{
    'name': 'Restricciones de Empleados en POS',
    'version': '18.0.1.2',
    'summary': 'Control de permisos y acceso de empleados en el Punto de Venta',
    'description': '''
        Módulo base para configurar y gestionar las restricciones de los cajeros en el Punto de Venta.
    ''',
    'category': 'Sales/Point of Sale',
    'author': 'Sensible Consulting Services, Crumges',
    'website': 'https://sensiblecs.com',
    'license': 'AGPL-3',
    'depends': ['pos_hr'],
    'data': [
        'views/sbl_hr_employee_view.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_hr_restriction/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
