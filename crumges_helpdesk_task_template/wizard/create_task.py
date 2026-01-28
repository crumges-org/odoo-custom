# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import re

class CreateTask(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'

    task_template_id = fields.Many2one(
        'project.task', 
        string='Template Task',
        domain="[('is_template', '=', True)]",
        help="Select a task to use as a template. Subtasks and configuration will be copied."
    )

    def action_generate_task(self):
        self.ensure_one()
        if not self.task_template_id:
            return super(CreateTask, self).action_generate_task()
        
        values = self._generate_task_values()
        values['is_template'] = False
        
        # Create new task by copying template
        # Note: We prioritize values from the wizard (including name)
        new_task = self.task_template_id.copy(default=values)
        
        # Explicitly enforce name in case copy() appended "(copy)"/("(copia)")
        if 'name' in values:
            new_task.write({'name': values['name']})
        
        # Subtasks handling:
        # If default copy() duplicated subtasks (depends on Odoo config), we clean their names.
        # If not, we manually copy them.
        if new_task.child_ids:
            self._clean_subtask_names(new_task.child_ids)
        elif self.task_template_id.child_ids:
            self._copy_subtasks(self.task_template_id, new_task)
            
        self.helpdesk_ticket_id.message_post_with_source(
            'helpdesk.ticket_conversion_link',
            render_values={'created_record': new_task, 'message': _('Task created')},
            subtype_xmlid='mail.mt_note',
        )
        
        return new_task

    def _copy_subtasks(self, src_task, parent_task):
        for child in src_task.child_ids:
            defaults = {
                'name': child.name, # Explicitly use original name
                'parent_id': parent_task.id,
                'project_id': parent_task.project_id.id,
            }
            new_child = child.copy(default=defaults)
            if child.child_ids:
                self._copy_subtasks(child, new_child)

    def _clean_subtask_names(self, tasks):
        # Recursively remove "(copy)" or "(copia)" from names
        for task in tasks:
            clean_name = re.sub(r'\s\((copy|copia)\)(\s\(\d+\))?$', '', task.name)
            if clean_name != task.name:
                task.write({'name': clean_name})
            
            if task.child_ids:
                self._clean_subtask_names(task.child_ids)
