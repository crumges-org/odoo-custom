/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    _getAllowedCategoryIds() {
        const cashier = this.pos?.cashier;
        if (!cashier) {
            return null;
        }

        // Usamos los IDs crudos (raw) para mayor velocidad y evitar problemas con Proxys de OWL
        const allowed_ids = cashier.raw?.allowed_pos_category_ids || [];
        if (!allowed_ids || allowed_ids.length === 0) {
            return null;
        }

        const allowedIds = new Set();
        const categoryModel = this.pos.models["pos.category"];
        if (!categoryModel) {
            return null;
        }

        for (const id of allowed_ids) {
            const cat = categoryModel.get(id);
            if (cat && typeof cat.getAllChildren === "function") {
                cat.getAllChildren().forEach((c) => {
                    if (c && c.id) {
                        allowedIds.add(c.id);
                    }
                });
            } else if (cat) {
                allowedIds.add(cat.id);
            }
        }
        return allowedIds.size > 0 ? allowedIds : null;
    },

    get products() {
        let products = super.products;
        try {
            const allowedIds = this._getAllowedCategoryIds();
            if (allowedIds) {
                // Optimización crítica: usar raw.pos_categ_ids para evitar iterar sobre registros
                return products.filter((p) => {
                    const productCategIds = p.raw?.pos_categ_ids || [];
                    for (const id of productCategIds) {
                        if (allowedIds.has(id)) {
                            return true;
                        }
                    }
                    return false;
                });
            }
        } catch (e) {
            console.error("Error en el filtrado de productos por empleado:", e);
        }
        return products;
    },

    getCategoriesAndSub() {
        const categories = super.getCategoriesAndSub();
        try {
            const allowedIds = this._getAllowedCategoryIds();
            if (allowedIds) {
                return categories.filter((c) => allowedIds.has(c.id));
            }
        } catch (e) {
            console.error("Error en el filtrado de categorías por empleado:", e);
        }
        return categories;
    },
});
