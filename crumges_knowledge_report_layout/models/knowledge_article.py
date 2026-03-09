from odoo import models, fields

class KnowledgeArticle(models.Model):
    _inherit = 'knowledge.article'

    report_config_id = fields.Many2one(
        'report.layout.config',
        string='Report Layout',
        help='Select a specific layout configuration for printing this article.'
    )
    
    use_custom_report_config = fields.Boolean(
        string='Use Custom Report Config',
        compute='_compute_use_custom_report_config',
        store=True,
        readonly=False,
        help='If checked, this article will use the selected report configuration.'
    )

    def _compute_use_custom_report_config(self):
        for article in self:
            if article.report_config_id:
                article.use_custom_report_config = True
            else:
                # Keep existing value if unchecked, or default to False
                if not article.use_custom_report_config:
                   article.use_custom_report_config = False
