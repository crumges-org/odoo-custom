/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosDB } from "@point_of_sale/app/store/db";

patch(PosDB.prototype, {
    add_brands(brands) {
        if (!this.brand_by_id) {
            this.brand_by_id = {};
        }
        for (const brand of brands) {
            this.brand_by_id[brand.id] = brand;
        }
    },
    get_brand_by_id(id) {
        return this.brand_by_id ? this.brand_by_id[id] : undefined;
    },
    get_brands() {
        return this.brand_by_id ? Object.values(this.brand_by_id) : [];
    },
    search_product_in_category(category_id, query) {
        let results = super.search_product_in_category(category_id, query);
        
        // Enhance search: if query matches brand name, include those products
        if (query) {
            const lowerQuery = query.toLowerCase();
            const brandIds = this.get_brands()
                .filter(b => b.name && b.name.toLowerCase().includes(lowerQuery))
                .map(b => b.id);
            
            if (brandIds.length > 0) {
                const products = this.product_by_id;
                for (const productId in products) {
                    const product = products[productId];
                    if (brandIds.includes(product.product_brand_id[0]) && !results.includes(product)) {
                        results.push(product);
                    }
                }
            }
        }
        return results;
    }
});
