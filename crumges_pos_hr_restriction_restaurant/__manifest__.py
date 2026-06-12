# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
{
    'name': 'Restricciones de Empleados en POS Restaurante',
    'version': '18.0.1.0',
    'summary': 'Control de permisos y acceso en el Punto de Venta de Restaurante',
    'description': '''
        Módulo para configurar y gestionar restricciones específicas de restaurantes para los cajeros en el Punto de Venta.
    ''',
    'category': 'Sales/Point of Sale',
    'author': 'Sensible Consulting Services, Crumges',
    'website': 'https://sensiblecs.com',
    'license': 'AGPL-3',
    'depends': ['crumges_pos_hr_restriction', 'pos_restaurant'],
    'auto_install': True,
    'data': [
        'views/sbl_hr_employee_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_hr_restriction_restaurant/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
