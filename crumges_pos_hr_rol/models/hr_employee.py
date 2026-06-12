# -*- coding: utf-8 -*-
from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        if 'role_name' not in fields:
            fields.append('role_name')
        if 'role_emoji' not in fields:
            fields.append('role_emoji')
        return fields
