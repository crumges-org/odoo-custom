from odoo import models, fields, api


class ProjectTaskCancelWizard(models.TransientModel):
    _name = 'project.task.cancel.wizard'
    _description = 'Wizard para confirmar cancelación de tareas'

    task_id = fields.Many2one('project.task', string='Tarea', required=True)
    message = fields.Html(string='Mensaje', compute='_compute_message')

    @api.depends('task_id')
    def _compute_message(self):
        for wizard in self:
            if wizard.task_id:
                children_count = len(wizard.task_id.child_ids)
                wizard.message = f"""
                    <div class="alert alert-warning">
                        <strong>⚠️ Advertencia</strong><br/>
                        Esta acción cancelará la tarea '<strong>{wizard.task_id.name}</strong>' 
                        y todas sus <strong>{children_count} subtareas</strong> que no tengan hojas de horas.<br/><br/>
                        ¿Desea continuar?
                    </div>
                """
            else:
                wizard.message = ""

    def action_confirm(self):
        self.ensure_one()
        self.task_id.with_context(cancel_confirmed=True).write({'state': '1_canceled'})
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}