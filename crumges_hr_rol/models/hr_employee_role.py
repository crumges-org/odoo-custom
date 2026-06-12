# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrEmployeeRole(models.Model):
    _name = 'hr.employee.role'
    _description = 'Rol de Empleado'

    name = fields.Char(string='Nombre del Rol', required=True, translate=True)
    role_emoji = fields.Char(string='Emoji/Icono', size=10, required=True, default='👤')
    description = fields.Text(string='Notas del Rol', translate=True)
    employee_ids = fields.One2many('hr.employee', 'role_id', string='Empleados')
    employee_count = fields.Integer(string='Cantidad de Empleados', compute='_compute_employee_count')

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    def action_view_employees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Empleados',
            'view_mode': 'list,kanban,form',
            'res_model': 'hr.employee',
            'domain': [('role_id', '=', self.id)],
            'context': {'default_role_id': self.id},
        }

    @api.depends('name', 'role_emoji')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.role_emoji:
                record.display_name = f"{record.role_emoji} {record.name}"
            else:
                record.display_name = record.name or ''
