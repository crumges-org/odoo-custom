import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    get isPricelistButtonDisabled() {
        const order = this.pos.get_order();
        return (
            this.pos.config.restrict_pricelist_change &&
            order &&
            order.get_orderlines().length > 0
        );
    },

    async clickPricelist() {
        const order = this.pos.get_order();
        if (
            !this.pos.config.restrict_pricelist_change &&
            order &&
            order.get_orderlines().length > 0
        ) {
            const proceed = await ask(this.dialog, {
                title: _t("Warning"),
                body: _t(
                    "You are about to change the pricelist with products in the cart. This will recalculate all prices, including weighable products. Do you want to continue?"
                ),
                confirmLabel: _t("Continue"),
                cancelLabel: _t("Cancel"),
            });
            if (!proceed) {
                return;
            }
        }
        return super.clickPricelist(...arguments);
    }
});
