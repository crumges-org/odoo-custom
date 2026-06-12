/** @odoo-module **/

import { EpsonPrinter } from "@pos_epson_printer/app/epson_printer";
import { patch } from "@web/core/utils/patch";
import { getLNATargetAddressSpace } from "@point_of_sale/app/utils/init_lna";

patch(EpsonPrinter.prototype, {
    setup({ ip }) {
        super.setup(...arguments);
        
        let protocol = odoo.use_lna ? "http:" : window.location.protocol;
        let cleanIp = ip;
        
        if (ip.startsWith("http://")) {
            protocol = "http:";
            cleanIp = ip.substring(7);
        } else if (ip.startsWith("https://")) {
            protocol = "https:";
            cleanIp = ip.substring(8);
        }
        
        this.url = protocol + "//" + cleanIp;
        this.address = this.url + "/cgi-bin/epos/service.cgi?devid=local_printer";
        if (odoo.use_lna) {
            this.lnaTargetAddressSpace = getLNATargetAddressSpace(this.address);
        }
    }
});
