from odoo import models, fields

class DocumentPage(models.Model):
    _inherit = 'document.page'

    report_config_id = fields.Many2one('report.layout.config', string="Report Template")
    use_custom_report_config = fields.Boolean(string="Use Custom Report Template", default=False)
