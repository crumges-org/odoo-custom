/** @odoo-module */

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

ProductCard.props = {
    ...ProductCard.props,
    brandImageUrl: { type: [String, Boolean], optional: true },
};
