/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        
        // Guardar las imagenes extra en el store
        if (loadedData['crumges.pos.product.image']) {
            this.crumges_pos_product_image_by_id = {};
            for (const img of loadedData['crumges.pos.product.image']) {
                this.crumges_pos_product_image_by_id[img.id] = img;
            }
        }
    }
});
