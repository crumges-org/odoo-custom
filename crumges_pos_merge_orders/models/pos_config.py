from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    merge_pricelist_behavior = fields.Selection(
        [
            ("block", "Bloquear Fusión (Seguro)"),
            ("ask", "Preguntar al Cajero (Recalcular)"),
            ("keep", "Mantener Precios Originales"),
        ],
        string="Comportamiento en Tarifas Mixtas",
        default="keep",
        required=True,
        help="Decide qué hacer si se fusionan pedidos con distintas listas de precios.",
    )
