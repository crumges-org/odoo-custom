# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    crumges_pos_image_ids = fields.One2many(
        'crumges.pos.product.image', 'product_tmpl_id', 
        string="Imágenes y Videos Adicionales (POS)"
    )
