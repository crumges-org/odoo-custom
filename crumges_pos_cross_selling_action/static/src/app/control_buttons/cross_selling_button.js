/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { CrossSellingPopup } from "@crumges_pos_cross_selling_action/app/popups/cross_selling_popup";

export class CrossSellingButton extends Component {
    static template = "crumges_pos_cross_selling_action.CrossSellingButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    get selectedOrderline() {
        return this.pos.get_order()?.get_selected_orderline();
    }

    get hasSuggestions() {
        const line = this.selectedOrderline;
        if (!line) return false;
        
        const product = line.get_product();
        if (!product) return false;

        const hasAlternatives = product.crumges_pos_alternative_variant_ids && product.crumges_pos_alternative_variant_ids.length > 0;
        const hasAccessories = product.crumges_pos_accessory_product_ids && product.crumges_pos_accessory_product_ids.length > 0;
        const hasOptionals = product.crumges_pos_optional_variant_ids && product.crumges_pos_optional_variant_ids.length > 0;

        return hasAlternatives || hasAccessories || hasOptionals;
    }

    async onClick() {
        const line = this.selectedOrderline;
        if (!line || !this.hasSuggestions) return;

        await this.popup.add(CrossSellingPopup, {
            product: line.get_product(),
        });
    }
}

ProductScreen.addControlButton({
    component: CrossSellingButton,
});
