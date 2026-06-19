from odoo import api, models, _

class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('commission.settlement') or _('New')
        return super().create(vals_list)
