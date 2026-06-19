/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        this.selectedBrandId = 0;
        this.showBrandMode = false;
    },
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (loadedData['product.brand']) {
            this.db.add_brands(loadedData['product.brand']);
        }
    },
    toggleBrandMode() {
        this.showBrandMode = !this.showBrandMode;
    },
    setSelectedBrandId(brandId) {
        this.selectedBrandId = brandId;
        this.showBrandMode = false;
        // Optionally reset category when selecting a brand
        this.setSelectedCategoryId(0);
    },
    getBrandSelectorItems() {
        // Devuelve las marcas simulando ser categorias para usar el mismo componente
        const brands = this.db.get_brands();
        let items = [{
            id: 0,
            name: "Todas las marcas",
            icon: "fa-tags",
            separator: "fa-caret-right",
            showSeparator: false,
        }];
        for (let brand of brands) {
            items.push({
                id: brand.id,
                name: brand.name,
                imageUrl: `/web/image?model=product.brand&field=logo&id=${brand.id}`,
                separator: "fa-caret-right",
                showSeparator: false,
            });
        }
        return items;
    },
    onCategorySelectorClick(id) {
        if (this.showBrandMode) {
            this.setSelectedBrandId(id);
        } else {
            this.setSelectedCategoryId(id);
        }
    }
});
