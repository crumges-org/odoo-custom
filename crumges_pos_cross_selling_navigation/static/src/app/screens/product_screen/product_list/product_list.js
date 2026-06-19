/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";

patch(ProductsWidget.prototype, {
    getCategories() {
        if (this.pos.crossSellingProduct && this.pos.selectedCategoryId < 0) {
            const product = this.pos.crossSellingProduct;
            let cats = [];
            
            // 1. Botón "Home" o Casita para volver al catálogo normal
            cats.push({
                id: 0,
                name: "",
                icon: "fa-home fa-2x",
                separator: "fa-caret-right",
                showSeparator: true,
                imageUrl: false,
            });
            
            // 2. Pestaña Principal de Sugerencias (ID -1)
            cats.push({
                id: -1,
                name: "Sugerencias: " + product.display_name,
                icon: "fa-star text-warning",
                separator: "fa-caret-right",
                showSeparator: this.pos.selectedCategoryId !== -1,
                imageUrl: false,
            });
            
            // 3. Pestañas Secundarias (solo si el producto tiene este tipo de sugerencia)
            if (product.crumges_pos_optional_variant_ids && product.crumges_pos_optional_variant_ids.length > 0) {
                cats.push({
                    id: -2,
                    name: "Opcionales",
                    icon: "fa-plus-circle",
                    separator: "fa-caret-right",
                    showSeparator: this.pos.selectedCategoryId !== -2,
                    imageUrl: false,
                });
            }
            if (product.crumges_pos_alternative_variant_ids && product.crumges_pos_alternative_variant_ids.length > 0) {
                cats.push({
                    id: -3,
                    name: "Alternativas",
                    icon: "fa-exchange",
                    separator: "fa-caret-right",
                    showSeparator: this.pos.selectedCategoryId !== -3,
                    imageUrl: false,
                });
            }
            if (product.crumges_pos_accessory_product_ids && product.crumges_pos_accessory_product_ids.length > 0) {
                cats.push({
                    id: -4,
                    name: "Accesorios",
                    icon: "fa-plug",
                    separator: "fa-caret-right",
                    showSeparator: this.pos.selectedCategoryId !== -4,
                    imageUrl: false,
                });
            }
            
            return cats;
        }
        return super.getCategories(...arguments);
    },
    
    get productsToDisplay() {
        if (this.pos.crossSellingProduct && this.pos.selectedCategoryId < 0) {
            const product = this.pos.crossSellingProduct;
            let list = [];
            
            const getProds = (ids) => {
                if (!ids) return [];
                return ids.map(id => this.pos.db.get_product_by_id(id)).filter(p => p);
            };
            
            const catId = this.pos.selectedCategoryId;
            
            if (catId === -1) {
                // Modo -1: Mostrar TODO junto
                list = [
                    ...getProds(product.crumges_pos_optional_variant_ids),
                    ...getProds(product.crumges_pos_alternative_variant_ids),
                    ...getProds(product.crumges_pos_accessory_product_ids)
                ];
                // Eliminar duplicados si los hubiese
                list = [...new Set(list)];
            } else if (catId === -2) {
                list = getProds(product.crumges_pos_optional_variant_ids);
            } else if (catId === -3) {
                list = getProds(product.crumges_pos_alternative_variant_ids);
            } else if (catId === -4) {
                list = getProds(product.crumges_pos_accessory_product_ids);
            }
            
            // Si hay filtro de búsqueda activo
            if (this.searchWord !== "") {
                const searchWordLowerCase = this.searchWord.toLowerCase();
                list = list.filter(p => 
                    p.display_name.toLowerCase().includes(searchWordLowerCase) || 
                    (p.barcode && p.barcode.includes(this.searchWord)) ||
                    (p.default_code && p.default_code.toLowerCase().includes(searchWordLowerCase))
                );
            }
            
            // Ordenar alfabéticamente
            return list.sort(function (a, b) {
                return a.display_name.localeCompare(b.display_name);
            });
        }
        
        return super.productsToDisplay;
    }
});
