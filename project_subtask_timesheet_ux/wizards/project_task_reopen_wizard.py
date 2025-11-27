from odoo import models, fields, api


class ProjectTaskReopenWizard(models.TransientModel):
    _name = 'project.task.reopen.wizard'
    _description = 'Wizard para confirmar reapertura de tareas'

    task_id = fields.Many2one('project.task', string='Tarea', required=True)
    target_state = fields.Selection([
        ('01_in_progress', 'En progreso'),
        ('02_changes_requested', 'Cambios solicitados'),
        ('03_approved', 'Aprobada'),
        ('1_done', 'Hecho'),
    ], string='Estado destino', required=True)
    reopen_children = fields.Boolean(string='Reabrir tareas hijas canceladas', default=True)
    message = fields.Html(string='Mensaje', compute='_compute_message')

    @api.depends('task_id')
    def _compute_message(self):
        for wizard in self:
            if wizard.task_id:
                canceled_count = len(wizard.task_id.child_ids.filtered(lambda t: t.state == '1_canceled'))
                wizard.message = f"""
                    <div class="alert alert-info">
                        <strong>ℹ️ Reapertura de tarea</strong><br/>
                        La tarea '<strong>{wizard.task_id.name}</strong>' tiene 
                        <strong>{canceled_count} subtareas canceladas</strong>.<br/><br/>
                        ¿Desea cambiar el estado de estas subtareas también?
                    </div>
                """
            else:
                wizard.message = ""

    def action_confirm(self):
        self.ensure_one()
        ctx = {
            'reopen_confirmed': True,
            'reopen_children': self.reopen_children,
            'target_state': self.target_state,
        }
        self.task_id.with_context(**ctx).write({'state': self.target_state})
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}