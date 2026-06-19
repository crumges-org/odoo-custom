# -*- coding: utf-8 -*-
{
    'name': "Relaciones Dinámicas",
    'summary': "Crea relaciones navegables entre cualquier documento de Odoo mediante Smart Buttons dinámicos",
    'author': "Crumges",
    'website': "https://crumges.com",
    'category': 'Productivity',
    'version': '18.0.1.0.0',
    'depends': ['base', 'web', 'mail', 'crumges_web_widget_fontawesome', 'crumges_web_widget_json_statinfo'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/relation_type_views.xml',
        'views/menu_views.xml',
        'wizard/relation_wizard_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
