# -*- coding: utf-8 -*-
from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        models_to_load = super()._pos_ui_models_to_load()
        if 'crumges.pos.product.image' not in models_to_load:
            models_to_load.append('crumges.pos.product.image')
        return models_to_load

    def _loader_params_crumges_pos_product_image(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name', 'sequence', 'image_1920', 'video_url', 'product_tmpl_id'],
            },
        }

    def _get_pos_ui_crumges_pos_product_image(self, params):
        return self.env['crumges.pos.product.image'].search_read(**params['search_params'])

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        if 'crumges_pos_image_ids' not in result['search_params']['fields']:
            result['search_params']['fields'].append('crumges_pos_image_ids')
        return result
