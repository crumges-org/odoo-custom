{
    'name': 'Ocultar Productos en Remito',
    'version': '18.0.1.0.0',
    'summary': 'Permite ocultar productos específicos (como packaging) en el reporte impreso de entrega.',
    'description': """
        Este módulo agrega una opción en la ficha del producto para ocultarlo en el reporte de entrega (Delivery Slip).
        Útil para componentes de Kits o packaging que se descuentan del stock pero no deben aparecer en el remito al cliente.
    """,
    'author': 'Crumges',
    'category': 'Inventory/Delivery',
    'depends': ['stock', 'product'],
    'data': [
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/report_delivery_document.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
