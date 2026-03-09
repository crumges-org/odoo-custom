from odoo import models, fields, api

class DocumentPageReportWizard(models.TransientModel):
    _name = 'document.page.report.wizard'
    _description = 'Print Document Page with Template'

    document_page_ids = fields.Many2many('document.page', string='Documents to Print')
    report_config_id = fields.Many2one('report.layout.config', string='Report Template')

    @api.model
    def default_get(self, fields):
        res = super(DocumentPageReportWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model == 'document.page' and active_ids:
             res['document_page_ids'] = [(6, 0, active_ids)]
        
        if 'report_config_id' in fields and self.env.context.get('active_id'):
             doc = self.env['document.page'].browse(self.env.context.get('active_id'))
             if doc.use_custom_report_config and doc.report_config_id:
                 res['report_config_id'] = doc.report_config_id.id
        return res

    def action_print_report(self):
        self.ensure_one()
        if not self.document_page_ids:
            return
        
        # Determine layout
        layout_id = self.report_config_id.id if self.report_config_id else None
        
        # Build URL for the first document (multi-print not supported nicely in one window usually)
        # We will redirect to the view of the first doc
        doc_id = self.document_page_ids[0].id
        
        url = f'/print/document_page/{doc_id}'
        if layout_id:
             url += f'?layout_id={layout_id}'
             
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
