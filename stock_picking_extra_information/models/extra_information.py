# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ExtraInformation(models.Model):
    _inherit = 'extra.information'

    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Picking',
        help='Stock Picking',
    )
