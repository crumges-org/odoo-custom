from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_report_delivery_automation = fields.Boolean(
        string="Automatizar Hitos/Entrega desde Tareas",
        help="Si se activa, el avance de las tareas generadas por este servicio reportará automáticamente "
             "el progreso en los Hitos de Venta o cantidades entregadas.",
        default=False
    )
