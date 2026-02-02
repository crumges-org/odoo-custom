{
    'name': 'MRP Potential Stock Visualization',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Displays potential stock quantity based on BOM components availability',
    'description': """
        This module adds a smart button to the product form and visual indicators in the Kanban view
        to show the potential quantity that can be manufactured based on the available stock
        of components defined in the Bill of Materials (BoM).
        
        Features:
        - Computes 'Potential Qty' for products with a valid Manufacturing BoM.
        - Smart Button on Product Form that links to the BoM Structure report.
        - Visual badge in Product Kanban view.
        - Strictly backend only; does not affect sales or delivery logic.
    """,
    'author': 'Crumges',
    'license': 'AGPL-3',
    'depends': ['mrp', 'stock', 'product'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
