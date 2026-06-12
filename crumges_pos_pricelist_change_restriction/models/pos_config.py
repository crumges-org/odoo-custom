# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    restrict_pricelist_change = fields.Boolean(
        string='Restrict Pricelist Change when cart has products',
        default=False,
        help='Restrict changing the pricelist if the cart is not empty.'
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        if fields and 'restrict_pricelist_change' not in fields:
            fields.append('restrict_pricelist_change')
        return fields
