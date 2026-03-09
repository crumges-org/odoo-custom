// @odoo-module

import { knowledgeTopbar } from "@knowledge/components/topbar/topbar";
import { patch } from "@web/core/utils/patch";

patch(knowledgeTopbar.component.prototype, {
    async onPrintWithTemplate() {
        const action = await this.orm.call('knowledge.report.wizard', 'get_action_for_article', [this.props.record.resId]);
        // Alternatively, since we know the action xmlid:
        this.actionService.doAction('crumges_knowledge_report_layout.action_knowledge_report_wizard', {
            additionalContext: {
                active_id: this.props.record.resId,
                active_ids: [this.props.record.resId],
                active_model: 'knowledge.article', // Ensure wizard knows the model
                default_article_ids: [this.props.record.resId]
            }
        });
    }
});
