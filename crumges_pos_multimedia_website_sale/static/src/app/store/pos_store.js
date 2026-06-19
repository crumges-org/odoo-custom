/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        
        if (loadedData['product.image']) {
            this.product_image_by_id = {};
            for (const img of loadedData['product.image']) {
                this.product_image_by_id[img.id] = img;
            }
        }
    }
});
