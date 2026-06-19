from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    crumges_pos_alternative_product_ids = fields.Many2many(
        'product.template', 'crumges_pos_product_alternative_rel', 'src_id', 'dest_id',
        string="Productos Alternativos POS",
        help="Sustitución / Upselling. Llévate este 'en lugar de' ese. Ej: Si no hay stock, ofrece este. O si buscan el Básico, ofréceles el Profesional."
    )
    
    crumges_pos_accessory_product_ids = fields.Many2many(
        'product.product', 'crumges_pos_product_accessory_rel', 'src_id', 'dest_id',
        string="Productos Accesorios POS",
        help="Venta Cruzada (Cross-selling). Llévate esto 'además de' ese. Ej: Compra un celular, ofrécele la funda."
    )
