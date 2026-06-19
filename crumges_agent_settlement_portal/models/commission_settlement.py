from odoo import api, models, _
from odoo import models, _

class CommissionSettlement(models.Model):
    _name = "commission.settlement"
    _inherit = ["commission.settlement", "portal.mixin"]

    def _compute_access_url(self):
        super()._compute_access_url()
        for settlement in self:
            settlement.access_url = '/my/settlements/%s' % (settlement.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return "Liquidacion-%s" % (self.name or "Nueva")

    def action_send_email(self):
        self.ensure_one()
        template = self.env.ref('crumges_agent_settlement_portal.email_template_commission_settlement', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        if template and template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'commission.settlement',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def preview_settlement(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
