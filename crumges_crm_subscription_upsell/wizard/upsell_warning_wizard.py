from odoo import api, fields, models, _
from markupsafe import Markup

class UpsellWarningWizard(models.TransientModel):
    _name = 'crumges.upsell.warning.wizard'
    _description = 'Upsell Warning Wizard'

    message = fields.Html(string='Message', readonly=True)
    subscription_id = fields.Many2one('sale.order', string='Subscription', required=True)
    
    def action_confirm_upsell(self):
        self.ensure_one()
        # Proceed with creating the upsell
        return self.subscription_id.with_context(skip_upsell_warning=True).action_upsell_from_lead()
