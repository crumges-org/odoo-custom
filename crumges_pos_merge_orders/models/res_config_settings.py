from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_merge_pricelist_behavior = fields.Selection(
        related="pos_config_id.merge_pricelist_behavior",
        readonly=False,
    )
