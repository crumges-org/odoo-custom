# Copyright 2025 Crumges
# License OPL-1 or later (https://www.odoo.com/documentation/17.0/legal/licenses.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zoom_api_key = fields.Char(
        string="Zoom API Key",
        config_parameter="crumges_elearning_videos.zoom_api_key",
    )
    zoom_api_secret = fields.Char(
        string="Zoom API Secret",
        config_parameter="crumges_elearning_videos.zoom_api_secret",
    )
