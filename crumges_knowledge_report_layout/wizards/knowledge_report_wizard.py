from odoo import models, fields, api

class KnowledgeReportWizard(models.TransientModel):
    _name = 'knowledge.report.wizard'
    _description = 'Print Knowledge Article with Template'

    article_ids = fields.Many2many('knowledge.article', string='Articles to Print')
    report_config_id = fields.Many2one('report.layout.config', string='Report Template')

    @api.model
    def default_get(self, fields):
        res = super(KnowledgeReportWizard, self).default_get(fields)
        if self.env.context.get('active_model') == 'knowledge.article' and self.env.context.get('active_ids'):
             res['article_ids'] = [(6, 0, self.env.context.get('active_ids'))]
        
        # Default report config from the first article if present
        if 'report_config_id' in fields and self.env.context.get('active_id'):
             article = self.env['knowledge.article'].browse(self.env.context.get('active_id'))
             if article.use_custom_report_config and article.report_config_id:
                 res['report_config_id'] = article.report_config_id.id
        return res

    def action_print_report(self):
        self.ensure_one()
        context = dict(self.env.context)
        # We pass the selected layout to the report context
        context.update({
            'kn_report_layout_id': self.report_config_id.id,
        })
        return self.env.ref('crumges_knowledge_report_layout.action_report_knowledge_article').with_context(context).report_action(self.article_ids)
