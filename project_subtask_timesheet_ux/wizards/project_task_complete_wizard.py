from odoo import models, fields, api


class ProjectTaskCompleteWizard(models.TransientModel):
    _name = 'project.task.complete.wizard'
    _description = 'Wizard para confirmar finalización forzada de tareas'

    task_id = fields.Many2one('project.task', string='Tarea', required=True)
    message = fields.Html(string='Mensaje', compute='_compute_message')
    pending_tasks_count = fields.Integer(string='Tareas Pendientes', compute='_compute_pending_tasks')
    pending_tasks_names = fields.Text(string='Nombres de Tareas', compute='_compute_pending_tasks')

    @api.depends('task_id')
    def _compute_pending_tasks(self):
        for wizard in self:
            if wizard.task_id:
                pending = wizard.task_id.child_ids.filtered(lambda t: t.state not in ['1_done', '1_canceled'])
                wizard.pending_tasks_count = len(pending)
                wizard.pending_tasks_names = "\n• ".join(pending.mapped('name'))
            else:
                wizard.pending_tasks_count = 0
                wizard.pending_tasks_names = ""

    @api.depends('task_id', 'pending_tasks_count', 'pending_tasks_names')
    def _compute_message(self):
        for wizard in self:
            if wizard.task_id and wizard.pending_tasks_count > 0:
                task_names_split = wizard.pending_tasks_names.split('\n• ')
                task_list_html = '</li><li>'.join(task_names_split)
                
                wizard.message = f"""
                    <div class="alert alert-warning">
                        <strong>⚠️ Advertencia: Finalización Forzada</strong><br/>
                        Esta acción marcará la tarea '<strong>{wizard.task_id.name}</strong>' como <strong>Hecho</strong> 
                        y cancelará las siguientes <strong>{wizard.pending_tasks_count} subtareas pendientes</strong>:<br/><br/>
                        <ul>
                            <li>{task_list_html}</li>
                        </ul>
                        <br/>
                        ¿Desea continuar?
                    </div>
                """
            else:
                wizard.message = ""

    def action_confirm(self):
        self.ensure_one()
        
        pending_count = self.pending_tasks_count
        task_name = self.task_id.name
        
        self.task_id._cascade_cancel_pending()
        self.task_id.with_context(auto_state_change=True).write({'state': '1_done'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Tarea Finalizada',
                'message': f'La tarea "{task_name}" se ha marcado como Hecho y se cancelaron {pending_count} subtareas pendientes.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}