from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    upsell_from_task = fields.Boolean(
        string="Upsell from Task",
        help="If checked, this product can be selected as an upsell in Project Tasks."
    )
