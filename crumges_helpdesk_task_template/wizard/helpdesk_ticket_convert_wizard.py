# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import re

class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = 'helpdesk.ticket.convert.wizard'

    task_template_id = fields.Many2one(
        'project.task', 
        string='Template Task',
        domain="[('is_template', '=', True)]",
        help="Select a task to use as a template. Subtasks and configuration will be copied."
    )

    def action_convert(self):
        if not self.task_template_id:
            return super(HelpdeskTicketConvertWizard, self).action_convert()
        
        tickets_to_convert = self._get_tickets_to_convert()
        created_tasks = self.env['project.task']
        
        for ticket in tickets_to_convert:
            vals = self._get_task_values(ticket)
            vals['is_template'] = False
            
            task = self.task_template_id.copy(default=vals)
            
            # Explicitly enforce name
            if 'name' in vals:
                task.write({'name': vals['name']})

            # Check duplication/manual copy
            if task.child_ids:
                self._clean_subtask_names(task.child_ids)
            elif self.task_template_id.child_ids:
                self._copy_subtasks(self.task_template_id, task)

            created_tasks += task
            
            ticket.active = False
            ticket_sudo, task_sudo = ticket.sudo(), task.sudo()
            ticket_sudo.message_post(body=_("Ticket converted into task %s", task_sudo._get_html_link()))
            task_sudo.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': task_sudo, 'origin': ticket_sudo},
                subtype_xmlid='mail.mt_note',
            )

        if len(created_tasks) == 1:
            return {
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id': created_tasks[0].id,
                'views': [(self.env.ref('project.view_task_form2').id, 'form')],
                'type': 'ir.actions.act_window',
            }
        return {
            'name': _('Converted Tasks'),
            'view_mode': 'list,form',
            'res_model': 'project.task',
            'views': [(self.env.ref('project.view_task_tree2').id, 'list'), (self.env.ref('project.view_task_form2').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', created_tasks.ids)],
        }
    
    def _copy_subtasks(self, src_task, parent_task):
        for child in src_task.child_ids:
            defaults = {
                'name': child.name,
                'parent_id': parent_task.id,
                'project_id': parent_task.project_id.id,
            }
            new_child = child.copy(default=defaults)
            if child.child_ids:
                self._copy_subtasks(child, new_child)

    def _clean_subtask_names(self, tasks):
        for task in tasks:
            clean_name = re.sub(r'\s\((copy|copia)\)(\s\(\d+\))?$', '', task.name)
            if clean_name != task.name:
                task.write({'name': clean_name})
            if task.child_ids:
                self._clean_subtask_names(task.child_ids)
