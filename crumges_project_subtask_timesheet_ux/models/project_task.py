from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    auto_log_timesheet = fields.Boolean(
        string='Registrar Horas Automáticamente',
        default=False,
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | {'auto_log_timesheet'}

    def _get_root_with_switch(self):
        self.ensure_one()
        current = self
        while current.parent_id:
            current = current.parent_id
        return current if current.sudo().auto_log_timesheet else None

    def _get_employee_for_timesheet(self, user):
        self.ensure_one()
        
        search_company = self.project_id.company_id if self.project_id.company_id else self.env.company
        
        employee = self.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id),
            ('company_id', '=', search_company.id)
        ], limit=1)
        
        if not employee:
            employee = self.env['hr.employee'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
        
        return employee

    def write(self, vals):
        if 'state' in vals and vals['state'] == '1_canceled' and not self.env.context.get('cancel_confirmed') and not self.env.context.get('auto_state_change'):
            for task in self:
                tasks_with_auto, tasks_with_manual = task._collect_tasks_with_timesheets()
                
                if tasks_with_auto or tasks_with_manual:
                    error_msg = f"No se puede cancelar la tarea '{task.name}':\n\n"
                    
                    if tasks_with_auto:
                        auto_names = "\n• ".join(tasks_with_auto.mapped('name'))
                        error_msg += f"Tareas con horas automáticas (cambie estado a 'En progreso'):\n• {auto_names}\n\n"
                    
                    if tasks_with_manual:
                        manual_names = "\n• ".join(tasks_with_manual.mapped('name'))
                        error_msg += f"Tareas con horas manuales (elimine las horas manualmente):\n• {manual_names}"
                    
                    raise UserError(error_msg)
                
                if task.child_ids:
                    # Automatic cascade cancel if no blocking hours
                    task._cascade_cancel()
        
        if 'state' in vals and vals['state'] == '1_canceled' and self.env.context.get('cancel_confirmed'):
            for task in self:
                task._cascade_cancel()
        
        if 'state' in vals and self.env.context.get('reopen_confirmed'):
            if self.env.context.get('reopen_children'):
                for task in self:
                    task._cascade_reopen()
        
        if 'state' in vals and not self.env.context.get('auto_state_change') and not self.env.context.get('reopen_confirmed'):
            for task in self:
                if task.state == '1_canceled' and vals['state'] != '1_canceled':
                    canceled_children = task.child_ids.filtered(lambda t: t.state == '1_canceled')
                    if canceled_children:
                        # Automatic cascade reopen
                        task._cascade_reopen()
        
        if 'state' in vals and not self.env.context.get('auto_state_change') and not self.env.context.get('reopen_confirmed'):
            is_manual_state_change = len(vals) == 1 or (len(vals) == 2 and 'kanban_state' in vals)
            
            if is_manual_state_change:
                for task in self:
                    root_with_switch = task._get_root_with_switch()
                    if root_with_switch and task.child_ids and task.state != '1_canceled' and vals['state'] != '1_canceled' and task.state != vals['state']:
                        raise UserError(
                            f"No se puede cambiar manualmente el estado de la tarea '{task.name}' "
                            f"porque la automatización está activa. El estado se actualiza automáticamente según sus subtareas."
                        )
        
        old_states = {}
        old_canceled = {}
        if 'state' in vals:
            for task in self:
                old_states[task.id] = task.state
                old_canceled[task.id] = task.state == '1_canceled'
        
        res = super(ProjectTask, self).write(vals)
        
        if 'state' in vals:
            for task in self:
                old_state = old_states.get(task.id)
                was_canceled = old_canceled.get(task.id, False)
                
                if not task.child_ids and not self.env.context.get('cancel_cascade'):
                    if old_state == '1_done' and task.state != '1_done':
                        task._remove_automatic_timesheet()
                    
                    if task.state == '1_done' and old_state != '1_done':
                        task._create_automatic_timesheet()
                
                if task.parent_id:
                    task.parent_id._recalculate_parent_state()
                
                if task.child_ids and was_canceled and task.state != '1_canceled':
                    task._recalculate_parent_state()
        
        if 'allocated_hours' in vals:
            for task in self:
                if task.child_ids:
                    task._recalculate_parent_state()
        
        if 'parent_id' in vals:
            for task in self:
                if task.parent_id:
                    task.parent_id._recalculate_parent_state()
        
        return res

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super(ProjectTask, self).create(vals_list)
        
        for task in tasks:
            if task.parent_id:
                task.parent_id._recalculate_parent_state()
        
        return tasks

    def unlink(self):
        parents = self.mapped('parent_id')
        res = super(ProjectTask, self).unlink()
        for parent in parents:
            if parent.exists():
                parent._recalculate_parent_state()
        return res

    def action_cancel_with_wizard(self):
        self.ensure_one()
        
        tasks_with_auto, tasks_with_manual = self._collect_tasks_with_timesheets()
        
        if tasks_with_auto or tasks_with_manual:
            error_msg = f"No se puede cancelar la tarea '{self.name}':\n\n"
            
            if tasks_with_auto:
                auto_names = "\n• ".join(tasks_with_auto.mapped('name'))
                error_msg += f"Tareas con horas automáticas (cambie estado a 'En progreso'):\n• {auto_names}\n\n"
            
            if tasks_with_manual:
                manual_names = "\n• ".join(tasks_with_manual.mapped('name'))
                error_msg += f"Tareas con horas manuales (elimine las horas manualmente):\n• {manual_names}"
            
            raise UserError(error_msg)
        
        wizard = self.env['project.task.cancel.wizard'].create({
            'task_id': self.id,
        })
        
        return {
            'name': 'Confirmar Cancelación',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.cancel.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reopen_with_wizard(self):
        self.ensure_one()
        
        canceled_children = self.child_ids.filtered(lambda t: t.state == '1_canceled')
        
        if self.state != '1_canceled' and not canceled_children:
            raise UserError("Esta acción solo está disponible para tareas canceladas o tareas con hijos cancelados.")
        
        target_state = '01_in_progress' if self.state == '1_canceled' else self.state
        
        wizard = self.env['project.task.reopen.wizard'].create({
            'task_id': self.id,
            'target_state': target_state,
        })
        
        return {
            'name': 'Confirmar Reapertura',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.reopen.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_force_complete_with_wizard(self):
        self.ensure_one()
        
        if not self.child_ids:
            raise UserError("Esta acción solo está disponible para tareas con subtareas.")
        
        if self.state == '1_done':
            raise UserError("La tarea ya está marcada como 'Hecho'.")
        
        pending_tasks = self.child_ids.filtered(lambda t: t.state not in ['1_done', '1_canceled'])
        
        if not pending_tasks:
            self.with_context(auto_state_change=True).write({'state': '1_done'})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Tarea Finalizada',
                    'message': f'La tarea "{self.name}" se ha marcado como Hecho.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        wizard = self.env['project.task.complete.wizard'].create({
            'task_id': self.id,
        })
        
        return {
            'name': 'Confirmar Finalización',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.complete.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _collect_tasks_with_timesheets(self):
        self.ensure_one()
        
        tasks_with_auto = self.env['project.task']
        tasks_with_manual = self.env['project.task']
        
        if not self.child_ids:
            all_timesheets = self.env['account.analytic.line'].search([
                ('task_id', '=', self.id)
            ])
            
            if all_timesheets:
                auto_timesheets = all_timesheets.filtered(
                    lambda t: t.name == f'Se completó: {self.name}'
                )
                manual_timesheets = all_timesheets - auto_timesheets
                
                if auto_timesheets:
                    tasks_with_auto = self
                if manual_timesheets:
                    tasks_with_manual = self
        else:
            for child in self.child_ids:
                child_auto, child_manual = child._collect_tasks_with_timesheets()
                tasks_with_auto |= child_auto
                tasks_with_manual |= child_manual
        
        return tasks_with_auto, tasks_with_manual

    def _cascade_cancel(self):
        self.ensure_one()
        
        if self.child_ids:
            for child in self.child_ids:
                child._cascade_cancel()
                child.with_context(auto_state_change=True, cancel_cascade=True).write({'state': '1_canceled'})

    def _cascade_cancel_pending(self):
        self.ensure_one()
        
        pending_children = self.child_ids.filtered(lambda t: t.state not in ['1_done', '1_canceled'])
        
        for child in pending_children:
            child._cascade_cancel_pending()
            child.with_context(auto_state_change=True, cancel_cascade=True).write({'state': '1_canceled'})

    def _cascade_reopen(self):
        self.ensure_one()
        
        if self.child_ids:
            for child in self.child_ids:
                if child.state == '1_canceled':
                    child._cascade_reopen()
                    child.with_context(auto_state_change=True).write({'state': '01_in_progress'})

    def _get_consumed_hours_for_task(self, task):
        timesheets = self.env['account.analytic.line'].search([
            ('task_id', '=', task.id)
        ])
        return sum(timesheets.mapped('unit_amount'))

    def _recalculate_parent_state(self):
        self.ensure_one()
        
        if not self.child_ids:
            return
        
        direct_children = self.child_ids.filtered(lambda t: t.allocated_hours and t.allocated_hours > 0)
        
        if not direct_children:
            return
        
        completed_children = direct_children.filtered(lambda t: t.state == '1_done')
        pending_children = direct_children.filtered(lambda t: t.state not in ['1_done', '1_canceled'])
        
        total_consumed_hours = sum(self._get_consumed_hours_for_task(child) for child in direct_children)
        parent_allocated_hours = self.allocated_hours or 0
        
        # Priority 1: Budget Exceeded -> Changes Requested
        if total_consumed_hours > parent_allocated_hours:
            if self.state != '02_changes_requested':
                _logger.info(f'Task {self.name}: horas consumidas ({total_consumed_hours}) exceden asignado ({parent_allocated_hours}), cambios solicitados')
                self.with_context(auto_state_change=True).write({'state': '02_changes_requested'})
            return

        # Priority 2: Pending Children -> In Progress
        if pending_children:
            if self.state in ['1_done', '03_approved', '02_changes_requested']:
                _logger.info(f'Task {self.name}: hay hijos sin completar, marcando como en progreso')
                self.with_context(auto_state_change=True).write({'state': '01_in_progress'})
            return
        
        # Priority 3: Budget Met/Under -> Done/Approved
        if total_consumed_hours == parent_allocated_hours:
            if self.state != '1_done':
                _logger.info(f'Task {self.name}: horas consumidas ({total_consumed_hours}) coinciden con asignado ({parent_allocated_hours}), hecho')
                self.with_context(auto_state_change=True).write({'state': '1_done'})
        else:
            if self.state != '03_approved':
                _logger.info(f'Task {self.name}: horas consumidas ({total_consumed_hours}) menores que asignado ({parent_allocated_hours}), aprobada')
                self.with_context(auto_state_change=True).write({'state': '03_approved'})

    def _remove_automatic_timesheet(self):
        self.ensure_one()
        
        root_with_switch = self._get_root_with_switch()
        
        if not root_with_switch:
            return
        
        if not self.allocated_hours or self.allocated_hours <= 0:
            return
        
        user_to_assign = self._get_user_for_timesheet()
        
        if not user_to_assign:
            return
        
        employee = self._get_employee_for_timesheet(user_to_assign)
        
        if not employee:
            return
        
        timesheet = self.env['account.analytic.line'].sudo().search([
            ('task_id', '=', self.id),
            ('employee_id', '=', employee.id),
            ('name', '=', f'Se completó: {self.name}')
        ], limit=1)
        
        if timesheet:
            _logger.info(f'Task {self.name}: eliminando timesheet automático')
            timesheet.unlink()
            
            if self.parent_id:
                self.parent_id._recalculate_parent_state()

    def _create_automatic_timesheet(self):
        self.ensure_one()
        
        root_with_switch = self._get_root_with_switch()
        
        if not root_with_switch:
            _logger.info(f'Task {self.name}: switch no activo en tarea raíz')
            return
        
        if not self.allocated_hours or self.allocated_hours <= 0:
            _logger.info(f'Task {self.name}: sin horas asignadas')
            return
        
        user_to_assign = self._get_user_for_timesheet()
        
        if not user_to_assign:
            _logger.info(f'Task {self.name}: sin usuario asignado, auto-asignando usuario actual')
            self.sudo().write({'user_ids': [(4, self.env.user.id)]})
            user_to_assign = self.env.user
        
        employee = self._get_employee_for_timesheet(user_to_assign)
        
        if not employee:
            _logger.warning(f'Task {self.name}: usuario sin empleado asociado')
            return
        
        existing_timesheet = self.env['account.analytic.line'].sudo().search([
            ('task_id', '=', self.id),
            ('employee_id', '=', employee.id),
            ('name', '=', f'Se completó: {self.name}')
        ], limit=1)
        
        if existing_timesheet:
            _logger.info(f'Task {self.name}: timesheet ya existe')
            return
        
        self.env['account.analytic.line'].sudo().create({
            'name': f'Se completó: {self.name}',
            'project_id': self.project_id.id,
            'task_id': self.id,
            'employee_id': employee.id,
            'company_id': employee.company_id.id,
            'unit_amount': self.allocated_hours,
            'date': fields.Date.context_today(self),
        })
        
        _logger.info(f'Task {self.name}: timesheet creado - {self.allocated_hours}h')
        
        if self.parent_id:
            self.parent_id._recalculate_parent_state()

    def _get_user_for_timesheet(self):
        self.ensure_one()
        
        if self.user_ids:
            return self.user_ids[0]
        
        return False


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def write(self, vals):
        tasks_to_recalc = self.mapped('task_id.parent_id')
        res = super(AccountAnalyticLine, self).write(vals)
        
        if 'unit_amount' in vals:
            for task in tasks_to_recalc:
                if task:
                    task._recalculate_parent_state()
        
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(AccountAnalyticLine, self).create(vals_list)
        
        tasks_to_recalc = lines.mapped('task_id.parent_id').filtered(lambda t: t)
        for task in tasks_to_recalc:
            task._recalculate_parent_state()
        
        return lines

    def unlink(self):
        tasks_to_recalc = self.mapped('task_id.parent_id')
        res = super(AccountAnalyticLine, self).unlink()
        
        for task in tasks_to_recalc:
            if task and task.exists():
                task._recalculate_parent_state()
        
        return res