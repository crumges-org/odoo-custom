/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        await super.afterProcessServerData(...arguments);
        // Exponemos la configuración globalmente para que BasePrinter pueda verla
        window.crumges_printer_emulator_active = this.config.crumges_printer_emulator_active;
        window.crumges_printer_pos_name = this.config.name || "Múltiples POS";
    }
});

patch(BasePrinter.prototype, {
    async printReceipt(receipt) {
        if (window.crumges_printer_emulator_active) {
            try {
                await fetch('/hw_proxy/print_xml_receipt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        params: {
                            pos_name: window.crumges_printer_pos_name,
                            receipt: document.createDocumentFragment().appendChild(receipt).innerHTML || receipt.outerHTML || (typeof receipt === 'string' ? receipt : "Custom receipt object")
                        }
                    })
                });
            } catch (e) {
                console.error("Emulator failed to send receipt", e);
            }
            return { successful: true };
        }
        return super.printReceipt(...arguments);
    },

    openCashbox() {
        if (window.crumges_printer_emulator_active) {
            return;
        }
        return super.openCashbox(...arguments);
    }
});
