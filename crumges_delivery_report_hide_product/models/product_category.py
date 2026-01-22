from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    hide_in_delivery_slip = fields.Boolean(
        string="Ocultar en Remito",
        help="Configuración por defecto para productos de esta categoría. "
             "Puede ser sobrescrita en cada producto individualmente."
    )
