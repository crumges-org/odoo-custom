#README.rst
===============================
Product Attribute Price Percentage
===============================

Este módulo permite definir un porcentaje de incremento sobre el precio de un producto en la tabla `product.template.attribute.value`.

**Características:**
--------------------
- Agrega un campo `price_percentage` para calcular automáticamente el `price_extra` en función del precio base del producto.
- Funciona de manera que el `price_extra` se actualiza según el `price_percentage`, pero el `price_percentage` no cambia cuando se modifica el precio del producto.
- Se integra con la vista de atributos del producto para facilitar su configuración.

**Uso:**
--------

1. Accede a la configuración de atributos de producto.
2. Define un porcentaje de incremento (`price_percentage`).
3. El sistema calculará automáticamente el precio adicional (`price_extra`).
4. Si el precio del producto cambia, el precio adicional se ajustará, pero el porcentaje se mantendrá.

**Mantenimiento:**
-----------------
Este módulo es desarrollado y mantenido por Crumges.

Para reportar errores o sugerencias, visita [Crumges](https://crumges.com).

