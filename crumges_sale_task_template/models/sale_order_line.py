from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        values = super()._timesheet_create_task_prepare_values(project)
        
        if self.product_id.task_template_id:
            template = self.product_id.task_template_id
            template_values = template._prepare_template_values_for_copy(project)
            values.update(template_values)
        
        return values

    def _timesheet_create_task(self, project):
        task = super()._timesheet_create_task(project)
        
        if task and self.product_id.task_template_id:
            template = self.product_id.task_template_id
            if template.child_ids:
                template._copy_subtasks_from_template(task)
        
        return task