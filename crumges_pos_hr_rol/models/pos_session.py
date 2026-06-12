# -*- coding: utf-8 -*-
from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_hr_employee(self):
        result = super()._loader_params_hr_employee()
        if 'role_name' not in result['search_params']['fields']:
            result['search_params']['fields'].append('role_name')
        return result
