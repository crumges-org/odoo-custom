/** @odoo-module */

import { useService } from '@web/core/utils/hooks';
import { Component, onWillStart, useState } from "@odoo/owl";

export class UserLimitDashboard extends Component {
    static template = "crumges_res_users_limit.UserLimitDashboard";
    static props = {};

    setup() {
        super.setup();
        this.orm = useService('orm');
        this.actionService = useService('action');
        this.notification = useService('notification');
        this.state = useState({
            data: null,
            max_licenses_input: 0
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const data = await this.orm.call("res.users.license", "get_dashboard_data", []);
        if (data.max_licenses > 0) {
            data.available_licenses = data.max_licenses - data.occupied_licenses;
        } else {
            data.available_licenses = 0;
        }
        this.state.data = data;
        this.state.max_licenses_input = data.max_licenses;
    }

    async updateMaxLicenses(ev) {
        const newLimit = parseInt(ev.target.value, 10);
        if (!isNaN(newLimit)) {
            try {
                const data = await this.orm.call("res.users.license", "update_max_licenses", [newLimit]);
                if (data.max_licenses > 0) {
                    data.available_licenses = data.max_licenses - data.occupied_licenses;
                } else {
                    data.available_licenses = 0;
                }
                this.state.data = data;
                this.state.max_licenses_input = data.max_licenses;
                this.notification.add("Límite de licencias actualizado correctamente", { type: "success" });
            } catch (error) {
                // If it fails (e.g. ValidationError), revert the visual input to the previous state
                ev.target.value = this.state.max_licenses_input;
            }
        }
    }

    async applyFilter(filterName) {
        const { actionId } = this.env.config;
        const action = actionId ? await this.actionService.loadAction(actionId) : {};
        
        if (action) {
            action['context'] = { [`search_default_${filterName}`]: 1 };
            return this.actionService.doAction(action, {clearBreadcrumbs: true});
        }
    }
}
