# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_restrict_pricelist_change = fields.Boolean(
        related='pos_config_id.restrict_pricelist_change',
        readonly=False,
        string='Restrict Pricelist Change when cart has products'
    )
