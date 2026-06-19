# -*- coding: utf-8 -*-
from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_print_brand = fields.Boolean(string="Print Brand on Receipt", default=True, help="Print the product brand on the receipt and order lines.")
