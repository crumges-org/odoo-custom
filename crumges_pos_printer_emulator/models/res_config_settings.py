# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_crumges_printer_emulator_active = fields.Boolean(
        related='pos_config_id.crumges_printer_emulator_active',
        readonly=False,
    )
    pos_crumges_printer_emulator_port = fields.Integer(
        related='pos_config_id.crumges_printer_emulator_port',
        readonly=False,
    )

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # When values change, try to apply emulator configuration
        self.env['pos.config']._start_or_stop_emulator()
