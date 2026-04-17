# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    # Campos que también vamos a exponer en settings
    crumges_printer_emulator_active = fields.Boolean(
        string='Enable Printer Emulator',
        help='If checked, it starts a local background server imitating a receipt printer proxy.'
    )
    crumges_printer_emulator_port = fields.Integer(
        string='Emulator Port',
        default=8070,
        help='Port used by the emulator HTTP server.'
    )

    def _register_hook(self):
        super()._register_hook()


    @api.model
    def _start_or_stop_emulator(self):
        # Native http controller doesnt need manual start/stop
        pass

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_config(self):
        result = super()._loader_params_pos_config()
        result['search_params']['fields'].append('crumges_printer_emulator_active')
        return result

