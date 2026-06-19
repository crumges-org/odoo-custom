/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/store/models";

patch(Orderline.prototype, {
    get_full_product_name() {
        let name = super.get_full_product_name(...arguments);
        if (this.pos.config.iface_print_brand && this.product.product_brand_id) {
            const brandId = this.product.product_brand_id[0];
            const brandName = this.product.product_brand_id[1] || (this.pos.db.get_brand_by_id(brandId) && this.pos.db.get_brand_by_id(brandId).name);
            if (brandName) {
                return `[${brandName}] ${name}`;
            }
        }
        return name;
    }
});
