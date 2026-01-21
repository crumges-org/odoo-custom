from odoo import fields, models

class TaskPurpose(models.Model):
    _name = 'task.purpose'
    _description = 'Task Purpose'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
