# -*- coding: utf-8 -*-
from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_clean_empty_orders = fields.Boolean(
        string='Limpiar Órdenes Vacías',
        default=False,
        help='Muestra un botón en la pantalla de órdenes para eliminar órdenes sin productos.'
    )
    clean_empty_orders_time_limit = fields.Integer(
        string='Tiempo de gracia (segundos)',
        default=10,
        help='Tiempo en segundos que debe transcurrir desde la creación de la orden para que pueda ser eliminada por el botón.'
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_iface_clean_empty_orders = fields.Boolean(
        related='pos_config_id.iface_clean_empty_orders',
        readonly=False,
    )
    pos_clean_empty_orders_time_limit = fields.Integer(
        related='pos_config_id.clean_empty_orders_time_limit',
        readonly=False,
    )
