from odoo import fields, models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allowed_pos_category_ids = fields.Many2many(
        'pos.category',
        string='Allowed POS Categories',
        help='If empty, the employee can see all categories.'
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields.append('allowed_pos_category_ids')
        return fields
