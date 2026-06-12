/** @odoo-module */

import { registry } from '@web/core/registry';
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { UserLimitDashboard } from '../components/user_limit_dashboard';

export class UserLimitDashboardListRenderer extends ListRenderer {
    static components = { ...ListRenderer.components, UserLimitDashboard };
    static template = "crumges_res_users_limit.DashboardListRenderer";
}

registry.category('views').add('user_limit_dashboard_tree', {
    ...listView,
    Renderer: UserLimitDashboardListRenderer,
});
