# -*- coding: utf-8 -*-
{
    'name': 'Project Subtask Visible by Default',
    'version': '18.0.1.0.2',
    'category': 'Project',
    'summary': 'Hace que las subtareas sean visibles por defecto al crearlas',
    'description': """
        Módulo para Odoo 18 - Visibilidad Automática de Subtareas
        ==========================================================
        
        Este módulo modifica el comportamiento predeterminado de las subtareas
        en el módulo de Proyectos de Odoo 18.
        
        Características:
        * Las subtareas se crean con visibilidad activada por defecto
        * No requiere configuración adicional
        * Funciona automáticamente al instalar
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        # Sin archivos de vistas - funcionamiento automático
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}