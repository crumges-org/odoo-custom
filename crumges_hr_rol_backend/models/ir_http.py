# -*- coding: utf-8 -*-
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super().session_info()
        user = self.env.user
        if user.employee_id and user.employee_id.role_emoji:
            res['employee_role_emoji'] = user.employee_id.role_emoji
            res['employee_role_name'] = user.employee_id.role_name
        return res
