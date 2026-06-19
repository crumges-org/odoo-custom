/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { CrossSellingPopup } from "@crumges_pos_cross_selling_popup/app/popups/cross_selling_popup";

patch(PosStore.prototype, {
    async addProductToCurrentOrder(product, options = {}) {
        // Verificar si el producto tiene sugerencias y no estamos previniendo el popup (por ejemplo, si venimos del popup mismo)
        const hasSuggestions = 
            (product.crumges_pos_alternative_variant_ids && product.crumges_pos_alternative_variant_ids.length > 0) ||
            (product.crumges_pos_accessory_product_ids && product.crumges_pos_accessory_product_ids.length > 0) ||
            (product.crumges_pos_optional_variant_ids && product.crumges_pos_optional_variant_ids.length > 0);

        const result = await super.addProductToCurrentOrder(product, options);

        if (hasSuggestions && !options.skip_cross_selling_popup && this.popup) {
            // Mostrar popup proactivo después de haber añadido el producto principal
            await this.popup.add(CrossSellingPopup, { product: product });
        }

        return result;
    }
});
