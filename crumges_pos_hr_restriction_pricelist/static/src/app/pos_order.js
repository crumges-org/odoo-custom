/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        const cashier = this.pos?.cashier;
        if (!cashier) return;

        let defaultPricelist = null;
        if (cashier.raw?.default_pos_pricelist_id) {
            const defaultId = Array.isArray(cashier.raw.default_pos_pricelist_id) ? cashier.raw.default_pos_pricelist_id[0] : cashier.raw.default_pos_pricelist_id;
            defaultPricelist = this.pos.models['product.pricelist'].get(defaultId);
        }

        const allowed_ids = cashier.raw?.allowed_pos_pricelist_ids || [];
        const hasAllowedList = allowed_ids && allowed_ids.length > 0;
        const allowedIdsSet = new Set(allowed_ids);

        if (defaultPricelist && (!hasAllowedList || allowedIdsSet.has(defaultPricelist.id))) {
            this.set_pricelist(defaultPricelist);
        } else if (hasAllowedList && this.pricelist_id && !allowedIdsSet.has(this.pricelist_id.id)) {
            let fallbackPricelist = null;
            if (this.config.pricelist_id && allowedIdsSet.has(this.config.pricelist_id.id)) {
                fallbackPricelist = this.config.pricelist_id;
            } else {
                fallbackPricelist = this.config.available_pricelist_ids.find(p => allowedIdsSet.has(p.id)) || null;
            }
            if (fallbackPricelist) {
                this.set_pricelist(fallbackPricelist);
            }
        }
    },

    updatePricelistAndFiscalPosition(newPartner) {
        super.updatePricelistAndFiscalPosition(newPartner);
        const cashier = this.pos?.cashier;
        if (!cashier) {
            return;
        }

        let defaultPricelist = null;
        if (cashier.raw?.default_pos_pricelist_id) {
            const defaultId = Array.isArray(cashier.raw.default_pos_pricelist_id) ? cashier.raw.default_pos_pricelist_id[0] : cashier.raw.default_pos_pricelist_id;
            defaultPricelist = this.pos.models['product.pricelist'].get(defaultId);
        }

        const allowed_ids = cashier.raw?.allowed_pos_pricelist_ids || [];
        if (!allowed_ids || allowed_ids.length === 0) {
            return;
        }
        const allowedIdsSet = new Set(allowed_ids);

        if (this.pricelist_id && !allowedIdsSet.has(this.pricelist_id.id)) {
            let fallbackPricelist = null;
            
            if (defaultPricelist && allowedIdsSet.has(defaultPricelist.id)) {
                fallbackPricelist = defaultPricelist;
            }

            if (!fallbackPricelist && this.config.pricelist_id && allowedIdsSet.has(this.config.pricelist_id.id)) {
                fallbackPricelist = this.config.pricelist_id;
            } else if (!fallbackPricelist) {
                fallbackPricelist = this.config.available_pricelist_ids.find(p => allowedIdsSet.has(p.id)) || null;
            }
            if (fallbackPricelist) {
                this.set_pricelist(fallbackPricelist);
            }
        }
    }
});
