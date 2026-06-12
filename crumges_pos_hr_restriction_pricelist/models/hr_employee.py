from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allowed_pos_pricelist_ids = fields.Many2many(
        'product.pricelist',
        string='Allowed POS Pricelists',
        help='If empty, the employee can see all pricelists.'
    )
    default_pos_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Default POS Pricelist',
        help='If set, this pricelist will be loaded by default for this employee in the Point of Sale.'
    )

    @api.constrains('default_pos_pricelist_id', 'allowed_pos_pricelist_ids')
    def _check_default_pricelist(self):
        for employee in self:
            if employee.allowed_pos_pricelist_ids and employee.default_pos_pricelist_id:
                if employee.default_pos_pricelist_id not in employee.allowed_pos_pricelist_ids:
                    raise ValidationError(_("La Lista de Precios por defecto debe estar incluida dentro de las Listas de Precios Permitidas."))

    @api.onchange('default_pos_pricelist_id', 'allowed_pos_pricelist_ids')
    def _onchange_default_pricelist(self):
        for employee in self:
            if employee.allowed_pos_pricelist_ids and employee.default_pos_pricelist_id:
                if employee.default_pos_pricelist_id not in employee.allowed_pos_pricelist_ids:
                    employee.allowed_pos_pricelist_ids = employee.allowed_pos_pricelist_ids + employee.default_pos_pricelist_id

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields.append('allowed_pos_pricelist_ids')
        fields.append('default_pos_pricelist_id')
        return fields
