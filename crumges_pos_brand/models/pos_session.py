# -*- coding: utf-8 -*-
from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'product.brand' not in result:
            result.append('product.brand')
        return result

    def _loader_params_product_brand(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['id', 'name'],
            },
        }

    def _get_pos_ui_product_brand(self, params):
        return self.env['product.brand'].search_read(**params['search_params'])

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        if 'product_brand_id' not in result['search_params']['fields']:
            result['search_params']['fields'].append('product_brand_id')
        return result
