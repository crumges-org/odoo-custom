/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class CrossSellingPopup extends AbstractAwaitablePopup {
    static template = "crumges_pos_cross_selling_popup.CrossSellingPopup";
    static defaultProps = {
        title: _t("Sugerencias POS"),
        cancelText: _t("Cerrar y Continuar"),
    };

    setup() {
        super.setup();
        this.pos = usePos();
    }

    get product() {
        return this.props.product;
    }

    getAlternativeProducts() {
        if (!this.product.crumges_pos_alternative_variant_ids) return [];
        return this.product.crumges_pos_alternative_variant_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    }

    getAccessoryProducts() {
        if (!this.product.crumges_pos_accessory_product_ids) return [];
        return this.product.crumges_pos_accessory_product_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    }

    getOptionalProducts() {
        if (!this.product.crumges_pos_optional_variant_ids) return [];
        return this.product.crumges_pos_optional_variant_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    }

    clickSuggestion(suggestedProduct) {
        this.pos.get_order().add_product(suggestedProduct);
        this.env.services.notification.add(_t("Producto agregado: %s", suggestedProduct.display_name), {
            type: "info",
        });
        // Opcional: cerrar el popup después de añadir
        // this.cancel();
    }
}
