# -*- coding: utf-8 -*-
{
    'name': "Limpieza de Órdenes Vacías en TPV",
    'summary': "Permite limpiar órdenes en 0 en la pantalla de tickets del Punto de Venta después de un tiempo configurado.",
    'description': """
Limpieza de Órdenes Vacías
===========================
Añade un botón en la pantalla de órdenes del Punto de Venta (TicketScreen) para eliminar de forma masiva aquellas órdenes que no tienen productos, respetando un tiempo de gracia desde su creación.
    """,
    'author': "Crumges",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_clean_empty_orders/static/src/overrides/ticket_screen.js',
            'crumges_pos_clean_empty_orders/static/src/overrides/ticket_screen.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
