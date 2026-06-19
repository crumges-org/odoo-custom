from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend([
            'crumges_pos_alternative_variant_ids',
            'crumges_pos_accessory_product_ids',
            'crumges_pos_optional_variant_ids',
        ])
        return result
