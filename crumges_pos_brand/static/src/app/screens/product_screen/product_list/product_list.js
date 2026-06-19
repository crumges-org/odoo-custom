/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";

patch(ProductsWidget.prototype, {
    get productsToDisplay() {
        let list = super.productsToDisplay;
        
        if (this.pos.selectedBrandId) {
            list = list.filter(product => 
                product.product_brand_id && product.product_brand_id[0] === this.pos.selectedBrandId
            );
        }
        
        return list;
    }
});
