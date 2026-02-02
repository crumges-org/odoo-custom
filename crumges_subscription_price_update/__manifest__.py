{
    'name': 'Subscription Price Update - Recálculo de Precios en Suscripciones',
    'version': '18.0.1.0.11',
    'category': 'Sales',
    'summary': 'Actualice precios en suscripciones activas con un clic. Módulo exclusivo para suscripciones.',
    'description': """
Subscription Price Update
=========================

Este módulo permite actualizar los precios de los productos en **Suscripciones Activas**.

Características Principales
---------------------------
*   **Exclusivo para Suscripciones:** Solo funciona en órdenes marcadas como recurrente (`is_recurring=True`) y que estén activas.
*   **Actualización Masiva:** Seleccione múltiples suscripciones y actualice sus precios.
*   **Vista Previa:** Visualice el impacto del cambio (Total Actual vs. Nuevo Total) antes de confirmar.
*   **Soporte de Precios Recurrentes:** Respeta la configuración de precios recurrentes del producto.

Uso
---
1.  Vaya a **Suscripciones > Suscripciones**.
2.  Seleccione una o varias suscripciones **activas**.
3.  En el menú **Acción**, seleccione **Recalculate Prices** (Recalcular Precios).
4.  Si seleccionó alguna orden que no es suscripción o no está activa, el sistema le avisará.
""",
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'sale_subscription'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mass_recalculate_prices_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/sale_subscription_price_update_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'maintainers': ['Crumges'],
}