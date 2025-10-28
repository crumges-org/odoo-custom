# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    has_upsell = fields.Boolean(string='Tiene Venta Adicional', default=False)
    upsell_product_id = fields.Many2one(
        'product.product', 
        string='Categoría de Venta Adicional',
        domain=[('is_upsell_category', '=', True)]
    )
    subscription_id = fields.Many2one('sale.order', string='Suscripción del Cliente')