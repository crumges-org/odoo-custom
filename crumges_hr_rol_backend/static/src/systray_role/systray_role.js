/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export class SystrayRole extends Component {
    static template = "crumges_hr_rol_backend.SystrayRole";
    
    get hasRole() {
        return !!session.employee_role_emoji;
    }
    
    get roleEmoji() {
        return session.employee_role_emoji;
    }
    
    get roleName() {
        return session.employee_role_name;
    }
}

registry.category("systray").add("crumges_hr_rol_backend.SystrayRole", {
    Component: SystrayRole,
}, { sequence: 0.1 });
