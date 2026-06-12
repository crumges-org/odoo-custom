/** @odoo-module */

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
    getPricelistList() {
        const selectionList = super.getPricelistList();
        const cashier = this.pos?.cashier;
        if (!cashier) {
            return selectionList;
        }
        const allowed_ids = cashier.raw?.allowed_pos_pricelist_ids || [];
        if (!allowed_ids || allowed_ids.length === 0) {
            return selectionList;
        }
        const allowedIdsSet = new Set(allowed_ids);
        return selectionList.filter((item) => {
            return item.id === null || allowedIdsSet.has(item.id);
        });
    }
});
