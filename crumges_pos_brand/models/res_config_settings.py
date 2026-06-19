# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_iface_print_brand = fields.Boolean(
        related='pos_config_id.iface_print_brand',
        readonly=False,
    )
