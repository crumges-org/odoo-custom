from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Sobrescribimos los campos del POS para que apunten a los de website_sale
    crumges_pos_alternative_product_ids = fields.Many2many(
        related='alternative_product_ids',
        readonly=False,
        help="Sincronizado con eCommerce"
    )
    
    crumges_pos_accessory_product_ids = fields.Many2many(
        related='accessory_product_ids',
        readonly=False,
        help="Sincronizado con eCommerce"
    )
