/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {
    //@override
    _getSearchFields() {
        if (!this.pos.config.module_pos_restaurant) {
            return super._getSearchFields(...arguments);
        }
        
        const searchFields = super._getSearchFields(...arguments);
        
        // Reemplazar la definición de TABLE por defecto de pos_restaurant
        if (searchFields.TABLE) {
            searchFields.TABLE = {
                repr: (order) => {
                    let tableName = "";
                    if (order.table_id) {
                        const table = order.getTable();
                        if (table) {
                            tableName = table.floor_id ? `${table.floor_id.name}/${table.getName()}` : table.getName();
                        } else {
                            tableName = order.table_id.getName() || "";
                        }
                    } else if (typeof order.getFloatingOrderName === "function") {
                        tableName = order.getFloatingOrderName();
                    }
                    return tableName || "";
                },
                displayName: _t("Table"),
                modelField: "table_id.table_number", // Mantenemos el modelo original por ahora, y controlamos la lógica en _computeSyncedOrdersDomain
            };
        }
        
        return searchFields;
    },

    //@override
    _computeSyncedOrdersDomain() {
        let { fieldName, searchTerm } = this.state.search;
        if (!searchTerm || fieldName !== "TABLE" || !this.pos.config.module_pos_restaurant) {
            return super._computeSyncedOrdersDomain(...arguments);
        }

        // Para la búsqueda de tabla en el backend
        const searchField = this._getSearchFields()[fieldName];
        if (searchField && searchField.formatSearch) {
            searchTerm = searchField.formatSearch(searchTerm);
        }

        // Si el término de búsqueda es numérico, podría estar buscando por el table_number.
        // Pero las floating orders se guardan usando el tracking_number o el pos_reference si el modelo pos.order no tiene floating_order_name
        // Nota: en Odoo 18 pos.order tiene el campo "table_id", pero "floating_order_name" no existe en la base de datos a menos que otro módulo lo haya añadido.
        // Si no existe el campo en el backend, buscar en 'pos_reference' y 'table_id.table_number'.
        // Pero las órdenes flotantes en pos_restaurant simplemente no tienen tabla. 
        // Su nombre flotante en Odoo suele venir del 'tracking_number' en el backend (ej. orden #...).
        
        // Vamos a construir un dominio 'OR' para abarcar table_number o tracking_number/narration
        const isNumeric = !isNaN(searchTerm) && !isNaN(parseFloat(searchTerm));
        let domain = [];

        if (isNumeric) {
            // Busca por número de mesa o nombre de ticket flotante
            domain = ['|', ['table_id.table_number', 'ilike', `%${searchTerm}%`], ['tracking_number', 'ilike', `%${searchTerm}%`]];
        } else {
            // Si es texto, `table_id.table_number` fallará en Postgres (es int).
            // Por ende, buscaremos sólo por el tracking_number u otros campos de texto que se usan para las float orders.
            // Si en Odoo 18, `pos.order` tiene un nombre especial, se usará ese (ej. tracking_number o pos_reference).
            domain = ['|', ['pos_reference', 'ilike', `%${searchTerm}%`], ['tracking_number', 'ilike', `%${searchTerm}%`]];
        }

        return domain;
    }
});
