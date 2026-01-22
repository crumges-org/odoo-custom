from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    delivery_slip_policy = fields.Selection(
        [
            ('default', 'Usar regla de categoría'),
            ('hide', 'Ocultar siempre'),
            ('show', 'Mostrar siempre')
        ],
        string="Política de Remito",
        default='default',
        required=True,
        help="Define cómo se comporta este producto en el remito de entrega:\n"
             "- Usar regla de categoría: Hereda el valor de la categoría.\n"
             "- Ocultar siempre: No aparece en el remito, ignorando la categoría.\n"
             "- Mostrar siempre: Aparece en el remito, ignorando la categoría."
    )

    hide_in_delivery_slip = fields.Boolean(
        string="Ocultar en Remito",
        compute='_compute_hide_in_delivery_slip',
        help="Indica si el producto se ocultará efectivamente en el remito, calculado en base a la política seleccionada."
    )

    @api.depends('delivery_slip_policy', 'categ_id.hide_in_delivery_slip')
    def _compute_hide_in_delivery_slip(self):
        for record in self:
            if record.delivery_slip_policy == 'hide':
                record.hide_in_delivery_slip = True
            elif record.delivery_slip_policy == 'show':
                record.hide_in_delivery_slip = False
            else:
                record.hide_in_delivery_slip = record.categ_id.hide_in_delivery_slip
