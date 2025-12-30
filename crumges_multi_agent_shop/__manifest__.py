{
    'name': 'Tienda Multi Agente Crumges',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Potencie a sus agentes: Permítales comprar por sus clientes directamente desde la web.',
    'description': """
Multi Agent Shop
================

Potencie a sus agentes: Permítales comprar por sus clientes directamente desde la web.

Este módulo extiende las capacidades del comercio electrónico permitiendo que "Agentes" autorizados inicien sesión y realicen pedidos en nombre de sus clientes.

Características Principales
---------------------------
*   **Compra Asistida:** El agente navega y compra, pero el pedido se registra para el cliente seleccionado.
*   **Selección de Cliente:** Interfaz dedicada para cambiar el "Cliente Activo" en cualquier momento.
*   **Trazabilidad:** Cada pedido guarda referencia tanto del cliente final como del agente que procesó la venta.
*   **Protección de Carrito:** Sistema inteligente que advierte y gestiona el carrito al cambiar de cliente para evitar errores.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'maintainers': ['Crumges'],
    'depends': [
        'sale',
        'website_sale',
        'base',
        'account',
    ],
    'data': [
        'data/website_menu_data.xml',
        'views/website_navbar_inherit.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/agent_shop_template.xml',
        'views/sale_order_cart_template.xml',
        'views/sale_order_portal_template.xml',
        'views/invoice_report_template.xml',
        'views/sale_order_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}