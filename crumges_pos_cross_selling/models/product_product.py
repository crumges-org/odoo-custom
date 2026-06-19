from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    crumges_pos_alternative_product_ids = fields.Many2many(
        related='product_tmpl_id.crumges_pos_alternative_product_ids',
        readonly=False
    )
    
    crumges_pos_alternative_variant_ids = fields.Many2many(
        'product.product',
        compute='_compute_pos_alternative_variant_ids',
        string="Variantes Alternativas POS"
    )
    
    crumges_pos_accessory_product_ids = fields.Many2many(
        related='product_tmpl_id.crumges_pos_accessory_product_ids',
        readonly=False
    )

    def _compute_pos_alternative_variant_ids(self):
        for product in self:
            variants = product.crumges_pos_alternative_product_ids.mapped('product_variant_ids')
            product.crumges_pos_alternative_variant_ids = variants.filtered(lambda p: p.available_in_pos)

    crumges_pos_optional_variant_ids = fields.Many2many(
        'product.product',
        compute='_compute_pos_optional_variant_ids',
        string="Variantes Opcionales POS"
    )

    def _compute_pos_optional_variant_ids(self):
        for product in self:
            # Leemos del campo nativo 'optional_product_ids' si existe (depende de sale)
            if hasattr(product, 'optional_product_ids'):
                variants = product.optional_product_ids.mapped('product_variant_ids')
                product.crumges_pos_optional_variant_ids = variants.filtered(lambda p: p.available_in_pos)
            else:
                product.crumges_pos_optional_variant_ids = False

