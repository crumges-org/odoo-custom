# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    role_id = fields.Many2one('hr.employee.role', string='Rol del Empleado')
    role_name = fields.Char(related='role_id.name', string='Nombre del Rol', readonly=True)
    role_emoji = fields.Char(related='role_id.role_emoji', string='Emoji del Rol', readonly=True)

    @api.depends('name', 'role_emoji')
    def _compute_display_name(self):
        super()._compute_display_name()
        for employee in self:
            if employee.role_emoji and employee.name:
                # Si el emoji ya está en el nombre (caso raro), no lo duplicamos
                if not employee.display_name.startswith(employee.role_emoji):
                    employee.display_name = f"{employee.role_emoji} {employee.display_name}"

