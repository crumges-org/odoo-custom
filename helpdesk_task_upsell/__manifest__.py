# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Ventas Adicionales en Suscripciones',
    'version': '18.0.2.0.0',
    'summary': """Gestión flexible de ventas adicionales y consumo de servicios pre-contratados en suscripciones mediante tareas FSM""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'category': 'Services/Helpdesk',
    'contributors': [
        'Crumges',
        'Alain Alvarez Caignet',
    ],
    'description': """
        Permite gestionar dos modalidades de servicios adicionales en suscripciones:
        - Venta Adicional Directa: Para servicios no contemplados
        - Consumo de Servicio Pre-contratado: Para servicios vendidos en bulk/bolsa de horas
        
        Características principales:
        - Categorías de servicio dinámicas y configurables
        - Creación automática de tareas o subtareas según el modo
        - Gestión de bolsas de horas pre-vendidas
        - Trazabilidad completa desde ticket hasta facturación
    """,
    'depends': [
        'helpdesk_fsm',
        'product',
        'sale_project',
        'sale_timesheet',
        'sale_subscription'
    ],
    'data': [
        'data/product_data.xml',
        'views/product_views.xml',
        'views/helpdesk_ticket_views.xml',
        'wizards/create_task_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'helpdesk_task_upsell/static/src/**/*'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
