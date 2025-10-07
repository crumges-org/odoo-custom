# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    extra_information_ids = fields.One2many(
        'extra.information',
        'sale_order_id',
        string='Extra Informations',
        required=False,
        tracking=True,
        )