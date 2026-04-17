# -*- coding: utf-8 -*-
{
    'name': "POS Printer Emulator",
    'summary': "Emulador de Impresora Interno para Point of Sale",
    'description': """
        Módulo que lanza un servidor HTTP local paralelo dentro del ecosistema Odoo
        para emular la presencia de una impresora térmica EPSON/Star u otra soportada por
        el Odoo IoT proxy. 
        Permite testear la funcionalidad `print_xml_receipt` generando logs 
        del contenido recibido, sin requerir hardware físico real.
    """,
    'author': "Crumges",
    'website': "https://www.crumges.com",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_printer_emulator/static/src/js/pos_store_patch.js',
        ]
    },
    'installable': True,
    'application': False,
}
