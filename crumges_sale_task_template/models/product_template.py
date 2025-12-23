from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    task_template_id = fields.Many2one(
        comodel_name='project.task',
        string='Task Template',
        domain="[('project_id', '!=', False)]",
        help='Task template to use when creating tasks from sales orders. '
             'The new task will replicate the configuration of this template.',
    )