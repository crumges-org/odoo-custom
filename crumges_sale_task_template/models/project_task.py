from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _prepare_template_values_for_copy(self, target_project):
        self.ensure_one()
        
        values = {
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'partner_id': self.partner_id.id,
            'user_ids': [(6, 0, self.user_ids.ids)],
            'description': self.description,
            'priority': self.priority,
            'sequence': self.sequence,
            'color': self.color,
        }
        
        return values

    def _copy_subtasks_from_template(self, new_task):
        self.ensure_one()
        
        for subtask in self.child_ids:
            subtask_vals = {
                'name': subtask.name,
                'project_id': new_task.project_id.id,
                'parent_id': new_task.id,
                'partner_id': new_task.partner_id.id,
                'tag_ids': [(6, 0, subtask.tag_ids.ids)],
                'allocated_hours': subtask.allocated_hours,
                'user_ids': [(6, 0, subtask.user_ids.ids)],
                'description': subtask.description,
                'priority': subtask.priority,
                'sequence': subtask.sequence,
                'color': subtask.color,
            }
            self.env['project.task'].create(subtask_vals)