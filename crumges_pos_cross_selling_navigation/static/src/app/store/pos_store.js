/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";

// 1. Interceptar selección de categoría para limpiar el estado si el usuario navega
patch(PosStore.prototype, {
    async setup() {
        const result = await super.setup(...arguments);
        this.crossSellingProduct = null; // Guardará el producto base de las sugerencias
        return result;
    },
    setSelectedCategoryId(categoryId) {
        // Si el usuario selecciona una categoría real (>= 0), salimos del modo sugerencias
        if (categoryId >= 0) {
            this.crossSellingProduct = null;
        }
        super.setSelectedCategoryId(categoryId);
    }
});

// 2. Interceptar selección de línea en el carrito para activar el modo sugerencias
patch(Order.prototype, {
    select_orderline(line) {
        super.select_orderline(line);
        if (line && line.product) {
            const product = line.product;
            const hasSuggestions = 
                (product.crumges_pos_alternative_variant_ids && product.crumges_pos_alternative_variant_ids.length > 0) ||
                (product.crumges_pos_accessory_product_ids && product.crumges_pos_accessory_product_ids.length > 0) ||
                (product.crumges_pos_optional_variant_ids && product.crumges_pos_optional_variant_ids.length > 0);

            if (hasSuggestions) {
                // Activar modo "Navegación Contextual de Venta Cruzada"
                this.pos.crossSellingProduct = product;
                // -1: Todas las Sugerencias
                this.pos.setSelectedCategoryId(-1);
            } else {
                // Si seleccionan un producto sin sugerencias estando en modo cruzado, salimos
                if (this.pos.crossSellingProduct) {
                    this.pos.crossSellingProduct = null;
                    if (this.pos.selectedCategoryId < 0) {
                        this.pos.setSelectedCategoryId(0); // Volver al inicio
                    }
                }
            }
        }
    }
});
