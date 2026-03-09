from odoo import http, _
from odoo.http import request

class DocumentPagePrintController(http.Controller):

    @http.route('/print/document_page/<int:doc_id>', type='http', auth="user")
    def print_document_page(self, doc_id, layout_id=None, **kwargs):
        document = request.env['document.page'].browse(doc_id)
        if not document.exists():
            return request.not_found()

        report_config = None
        if layout_id:
            report_config = request.env['report.layout.config'].browse(int(layout_id))
        elif document.use_custom_report_config and document.report_config_id:
            report_config = document.report_config_id

        values = {
            'doc': document,
            'report_config': report_config,
            'user': request.env.user,
            'company': request.env.company,
        }
        return request.render('crumges_document_page_report_layout.document_page_print_view', values)
