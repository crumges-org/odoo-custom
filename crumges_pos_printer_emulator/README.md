# POS Printer Emulator (crumges_pos_printer_emulator)

Este módulo de Odoo 18 levanta un servidor HTTP local en un hilo paralelo dentro de Odoo. Su propósito es actuar como un "Proxy IoT" emulado para capturar las peticiones de impresión de recibos (XML) que envía el Point of Sale.

## Requisitos
- No requiere dependencias externas más allá de las integradas en Odoo (usa `werkzeug`).
- Debe correr en entornos Odoo 18 (Community / Enterprise).

## Configuración y Uso

1. Instale el módulo en su instancia de Odoo 18.
2. Navegue a **Punto de Venta > Configuración > Ajustes**.
3. Busque la sección de Dispositivos Conectados / Emulador.
4. Marque la casilla **Enable Printer Emulator** y asigne un puerto libre (por defecto `8070`). Guarde los cambios.
5. Vaya a la configuración de su Caja/Punto de Venta.
6. En la opción **Receipt Printer** (Impresora de recibos), en **IP Address**, coloque `localhost:8070` (o la IP/Puerto donde corre Odoo y que configuró en el paso 4).
7. Al realizar un pedido de prueba y pulsar Imprimir, el XML no irá a una impresora física, sino que quedará registrado en `/tmp/crumges_printer_emulator.log`.

### Visor Web
Para visualizar el último ticket enviado al emulador de forma cómoda en el navegador web:
- Navegue a: `http://localhost:8070/crumges/last_receipt`
