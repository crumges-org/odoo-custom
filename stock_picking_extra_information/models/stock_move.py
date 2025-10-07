# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.picking'

    extra_information_ids = fields.One2many(
        'extra.information',
        'stock_picking_id',
        string='Extra Informations',
        required=False,
        tracking=True,
        compute='_compute_extra_information_ids',
        store=True,
        readonly=False,
    )

    @api.depends('sale_id')
    def _compute_extra_information_ids(self):
        for record in self:
            if record.sale_id:
                record.extra_information_ids = \
                    record.sale_id.extra_information_ids + \
                    record.extra_information_ids
            else:
                record.extra_information_ids = record.extra_information_ids
