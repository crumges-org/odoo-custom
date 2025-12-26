{
    'name': 'Sale Confirmed Price Update - Recálculo de Precios en Ventas Confirmadas',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Permite recalcular los precios de líneas de pedido en ventas confirmadas. Actualización masiva de precios.',
    'description': """
Recálculo de Precios en Ventas Confirmadas
==========================================

Este módulo permite actualizar los precios de los productos en pedidos de venta que ya han sido confirmados. Es especialmente útil cuando cambian las tarifas y se necesita aplicar los nuevos precios a pedidos pendientes de facturar o entregar.

Características Principales
---------------------------
*   **Actualización Masiva:** Seleccione múltiples pedidos de venta y actualice sus precios de una sola vez.
*   **Vista Previa:** Visualice el impacto del cambio de precios (Total Actual vs. Nuevo Total) antes de confirmar.
*   **Detalle por Línea:** Opción para ver el detalle de cambios línea por línea.
*   **Soporte de Promociones:** Si utiliza el módulo de promociones de Odoo, también recalcula los descuentos y recompensas.
*   **Wizard Intuitivo:** Interfaz fácil de usar para gestionar las actualizaciones.

Uso
---
1.  Vaya a **Ventas > Pedidos > Pedidos**.
2.  Seleccione uno o varios pedidos confirmados.
3.  En el menú **Acción**, seleccione **Recalculate Prices** (Recalcular Precios).
4.  Revise los cambios en el asistente y confirme.

Autor
-----
*   Crumges

Mantenedor
----------
Este módulo es mantenido por Crumges.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mass_recalculate_prices_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'maintainers': ['Crumges'],
}