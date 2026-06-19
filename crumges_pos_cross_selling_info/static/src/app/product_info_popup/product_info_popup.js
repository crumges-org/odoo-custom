/** @odoo-module */

import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductInfoPopup.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        // Ocultar la sección nativa de Odoo limpiando el array
        // La plantilla nativa usa "optional_products.length > 0", por lo que un array vacío evita que renderice la caja vacía y no lanza error.
        if (this.props.productInfo && this.props.productInfo.optional_products) {
            this.props.productInfo.optional_products = [];
        }
    },

    getAlternativeProducts(product) {
        if (!product.crumges_pos_alternative_variant_ids) return [];
        return product.crumges_pos_alternative_variant_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    },

    getAccessoryProducts(product) {
        if (!product.crumges_pos_accessory_product_ids) return [];
        return product.crumges_pos_accessory_product_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    },

    getOptionalProducts(product) {
        if (!product.crumges_pos_optional_variant_ids) return [];
        return product.crumges_pos_optional_variant_ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
    },

    clickSuggestion(product) {
        // En lugar de solo mostrar la info, podemos agregarlo directamente al carrito o abrir su propia info.
        // Aquí vamos a añadirlo al carrito para hacer la venta cruzada efectiva.
        this.pos.get_order().add_product(product);
        // Opcional: mostrar una notificación o simplemente cerrar el popup.
        this.props.close();
    }
});
