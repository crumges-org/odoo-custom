# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    # Campos heredados del template para categorías de upsell
    is_upsell_category = fields.Boolean(
        related='product_tmpl_id.is_upsell_category',
        readonly=False,
        store=True
    )
    
    upsell_mode = fields.Selection(
        related='product_tmpl_id.upsell_mode',
        readonly=False,
        store=True
    )
    
    parent_service_product_id = fields.Many2one(
        related='product_tmpl_id.parent_service_product_id',
        readonly=False,
        store=True
    )
    
    dummy_product_id = fields.Many2one(
        related='product_tmpl_id.dummy_product_id',
        readonly=False,
        store=True
    )
