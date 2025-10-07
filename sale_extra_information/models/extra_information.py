# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ExtraInformation(models.Model):
    _inherit = 'extra.information'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        help='Sale Order',
    )
