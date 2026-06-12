/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    set_cashier(employee) {
        super.set_cashier(employee);
        const order = this.get_order();
        if (!order || !employee) return;

        let defaultPricelist = null;
        if (employee.raw?.default_pos_pricelist_id) {
            const defaultId = Array.isArray(employee.raw.default_pos_pricelist_id) ? employee.raw.default_pos_pricelist_id[0] : employee.raw.default_pos_pricelist_id;
            defaultPricelist = this.models['product.pricelist'].get(defaultId);
        }

        const allowed_ids = employee.raw?.allowed_pos_pricelist_ids || [];
        const hasAllowedList = allowed_ids && allowed_ids.length > 0;
        const allowedIdsSet = new Set(allowed_ids);

        const orderPricelist = order.pricelist_id;
        const isOrderEmpty = order.get_orderlines().length === 0;

        let shouldUpdate = false;
        let newPricelist = null;

        if (defaultPricelist && isOrderEmpty) {
            if (!hasAllowedList || allowedIdsSet.has(defaultPricelist.id)) {
                shouldUpdate = true;
                newPricelist = defaultPricelist;
            }
        } else if (hasAllowedList && orderPricelist && !allowedIdsSet.has(orderPricelist.id)) {
            shouldUpdate = true;
            if (defaultPricelist && allowedIdsSet.has(defaultPricelist.id)) {
                newPricelist = defaultPricelist;
            } else if (this.config.pricelist_id && allowedIdsSet.has(this.config.pricelist_id.id)) {
                newPricelist = this.config.pricelist_id;
            } else {
                newPricelist = this.config.available_pricelist_ids.find(p => allowedIdsSet.has(p.id)) || null;
            }
        }

        if (shouldUpdate && newPricelist) {
            order.set_pricelist(newPricelist);
        }
    }
});
