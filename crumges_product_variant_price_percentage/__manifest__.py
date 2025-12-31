# -*- coding: utf-8 -*-
{
    'name': 'Product Variant Price Percentage',
    'summary': 'Sincronización total de precios. Porcentajes que reaccionan automáticamente a los cambios del mercado.',
    'description': """
Product Variant Price Percentage
================================

Sincronización total de precios. Porcentajes que reaccionan automáticamente a los cambios del mercado.

Sincronización bidireccional inteligente y actualización automática en tiempo real.

Características Avanzadas
-------------------------
*   **Sincronización Bidireccional:** Edite % o monto fijo, ambos se actualizan.
*   **Live Updates:** Cambio de precio base dispara recálculo automático de variantes.
*   **Precisión:** Cálculos exactos sin intervención manual.
""",
    'version': '18.0.1.0.0',
    'category': 'Product',
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': ['product'],
    'data': [
        'views/product_attribute_value_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {},
}
