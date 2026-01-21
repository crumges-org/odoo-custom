from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    task_id = fields.Many2one('project.task', string='Related Task')

    def write(self, vals):
        # Prevent manual name change if linked to a task
        if 'name' in vals:
            for line in self:
                if line.task_id and vals['name'] != line.task_id.name:
                     vals['name'] = line.task_id.name
        return super().write(vals)
