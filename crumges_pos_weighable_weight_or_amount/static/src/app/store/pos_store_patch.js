import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { WeightAmountPopup } from "../weight_amount_popup/weight_amount_popup";
import { getTaxesAfterFiscalPosition } from "@point_of_sale/app/models/utils/tax_utils";

patch(PosStore.prototype, {
    async addLineToOrder(vals, order, opts = {}, configure = true) {
        const product = typeof vals.product_id === "number" 
            ? this.data.models["product.product"].get(vals.product_id) 
            : vals.product_id;

        // Intercept manually selected weighable products (not via barcode)
        if (product.to_weight && !opts.code && configure) {
            const pricelist = this.getDefaultPricelist();
            const rawPrice = product.get_price(pricelist, 1);
            let taxes = product.taxes_id;
            if (order && order.fiscal_position_id) {
                taxes = getTaxesAfterFiscalPosition(taxes, order.fiscal_position_id, this.models);
            }
            const hasIncludedTax = taxes.some(tax => tax.price_include);
            const taxesData = this.getProducePriceDetails(product, rawPrice);
            const price = hasIncludedTax ? taxesData.total_included : taxesData.total_excluded;
            const priceFormatted = this.env.utils.formatCurrency(price);
            const payload = await new Promise((resolve) => {
                this.dialog.add(WeightAmountPopup, {
                    product: product,
                    price: price,
                    priceFormatted: priceFormatted,
                    currencySymbol: this.getCurrencySymbol(),
                    getPayload: (data) => resolve(data),
                    close: () => resolve(null),
                });
            });

            if (payload) {
                vals.qty = payload.weight;
                // Continue adding the line but with configure=false to avoid re-triggering this or standard weight popups
                const line = await super.addLineToOrder(vals, order, opts, false);
                if (line && payload.targetAmount !== undefined) {
                    const targetAmount = parseFloat(payload.targetAmount);
                    const qty = line.get_quantity();
                    if (targetAmount > 0 && qty > 0) {
                        const calculatedUnitPrice = targetAmount / qty;
                        line.set_unit_price(calculatedUnitPrice);

                        // Bucle de retroalimentación para corregir discrepancias por micro-redondeo
                        const getLineTotal = () => {
                            const prices = line.get_all_prices();
                            return hasIncludedTax ? prices.priceWithTax : prices.priceWithoutTax;
                        };

                        const dp = this.models["decimal.precision"].find((dp) => dp.name === "Product Price");
                        const digits = dp ? dp.digits : 2;
                        const stepSize = Math.pow(10, -digits);
                        const epsilon = 0.005; // Tolerancia de medio centavo

                        let currentTotal = getLineTotal();
                        let diff = targetAmount - currentTotal;
                        let iterations = 0;

                        while (Math.abs(diff) > epsilon && iterations < 5) {
                            const step = Math.sign(diff) * stepSize;
                            line.set_unit_price(line.price_unit + step);
                            currentTotal = getLineTotal();
                            diff = targetAmount - currentTotal;
                            iterations++;
                        }
                    }
                }
                return line;
            } else {
                // User cancelled the popup
                return null;
            }
        }

        return await super.addLineToOrder(...arguments);
    }
});
