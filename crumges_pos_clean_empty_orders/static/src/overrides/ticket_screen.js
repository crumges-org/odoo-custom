/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(TicketScreen.prototype, {
    cleanEmptyOrders() {
        const orders = this.pos.models["pos.order"].filter((o) => !o.finalized);
        const now = Date.now();
        const timeLimitMs = (this.pos.config.clean_empty_orders_time_limit || 10) * 1000;
        
        // Copiamos el arreglo para evitar problemas de índices al eliminar elementos
        const ordersToCheck = [...orders];

        for (const order of ordersToCheck) {
            // Verificamos si no tiene líneas de pedido
            if (order.get_orderlines().length === 0) {
                // En Odoo 18, date_order es directamente accesible en el modelo
                const dateStr = order.date_order || order.creation_date;
                let orderTimeMs = now;
                
                if (dateStr) {
                    // Si es el formato de odoo clásico 'YYYY-MM-DD HH:MM:SS', lo preparamos para parseo nativo
                    const safeDateStr = (typeof dateStr === 'string') ? dateStr.replace(' ', 'T') : dateStr;
                    // Asumimos UTC como lo maneja Odoo por defecto en la base de datos
                    orderTimeMs = new Date(safeDateStr + (safeDateStr.includes('Z') ? '' : 'Z')).getTime(); 
                    if (isNaN(orderTimeMs)) {
                        orderTimeMs = new Date(dateStr).getTime();
                    }
                }

                if (!isNaN(orderTimeMs)) {
                    // Calculamos la diferencia
                    if ((now - orderTimeMs) >= timeLimitMs) {
                        this.pos.removeOrder(order);
                    }
                }
            }
        }
    }
});
