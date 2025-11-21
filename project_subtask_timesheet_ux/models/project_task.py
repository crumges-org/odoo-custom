from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    auto_log_timesheet = fields.Boolean(
        string='Registrar Horas Automáticamente',
        default=False,
    )

    def write(self, vals):
        old_states = {}
        if 'state' in vals:
            for task in self:
                old_states[task.id] = task.state
        
        res = super(ProjectTask, self).write(vals)
        
        if 'state' in vals:
            for task in self:
                old_state = old_states.get(task.id)
                
                if old_state == '1_done' and task.state != '1_done':
                    task._remove_automatic_timesheet()
                
                if task.state in ['1_done', '1_canceled'] and old_state != '1_done':
                    task._create_automatic_timesheet()
                
                if task.parent_id:
                    if task.state == '1_done':
                        task.parent_id._check_all_subtasks_done()
                    else:
                        task.parent_id._check_subtasks_status()
        
        if 'parent_id' in vals:
            for task in self:
                if task.parent_id and task.parent_id.state in ['1_done', '03_approved', '02_changes_requested']:
                    task.parent_id._reopen_parent_task()
        
        return res

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super(ProjectTask, self).create(vals_list)
        
        for task in tasks:
            if task.parent_id and task.parent_id.state in ['1_done', '03_approved', '02_changes_requested']:
                task.parent_id._reopen_parent_task()
        
        return tasks

    def _check_subtasks_status(self):
        self.ensure_one()
        
        if not self.child_ids:
            return
        
        all_done = all(child.state == '1_done' for child in self.child_ids)
        
        if not all_done and self.state in ['1_done', '03_approved', '02_changes_requested']:
            _logger.info(f'Task {self.name}: hay subtareas sin completar, marcando como en progreso')
            self.write({'state': '01_in_progress'})

    def _check_all_subtasks_done(self):
        self.ensure_one()
        
        if not self.child_ids:
            return
        
        all_done = all(child.state == '1_done' for child in self.child_ids)
        
        if not all_done:
            return
        
        total_subtask_hours = sum(child.allocated_hours for child in self.child_ids)
        parent_allocated_hours = self.allocated_hours or 0
        
        if total_subtask_hours > parent_allocated_hours:
            _logger.info(f'Task {self.name}: todas las subtareas completadas pero se excedió el tiempo asignado, marcando como cambios solicitados')
            self.write({'state': '02_changes_requested'})
        elif total_subtask_hours >= parent_allocated_hours:
            _logger.info(f'Task {self.name}: todas las subtareas completadas y tiempo consumido, marcando como hecha')
            self.write({'state': '1_done'})
        else:
            _logger.info(f'Task {self.name}: todas las subtareas completadas pero falta tiempo por asignar, marcando como aprobada')
            self.write({'state': '03_approved'})

    def _reopen_parent_task(self):
        self.ensure_one()
        
        if self.state in ['1_done', '03_approved', '02_changes_requested']:
            _logger.info(f'Task {self.name}: nueva subtarea agregada, reabriendo tarea padre')
            self.write({'state': '01_in_progress'})

    def _remove_automatic_timesheet(self):
        self.ensure_one()
        
        if self.child_ids:
            _logger.info(f'Task {self.name}: es una tarea padre con hijos, no se elimina timesheet')
            return
        
        should_remove = False
        
        if self.parent_id and self.parent_id.auto_log_timesheet:
            should_remove = True
        elif not self.parent_id and self.auto_log_timesheet:
            should_remove = True
        
        if not should_remove:
            _logger.info(f'Task {self.name}: auto_log_timesheet no está activo, no se elimina timesheet')
            return
        
        user_to_assign = self._get_user_for_timesheet()
        
        if not user_to_assign:
            return
        
        employee = self.env['hr.employee'].search([
            ('user_id', '=', user_to_assign.id)
        ], limit=1)
        
        if not employee:
            return
        
        timesheet = self.env['account.analytic.line'].search([
            ('task_id', '=', self.id),
            ('employee_id', '=', employee.id),
            ('name', '=', f'Se completó: {self.name}')
        ], limit=1)
        
        if timesheet:
            _logger.info(f'Task {self.name}: eliminando timesheet automático ID {timesheet.id}')
            timesheet.unlink()

    def _create_automatic_timesheet(self):
        self.ensure_one()
        
        if self.child_ids:
            _logger.info(f'Task {self.name}: es una tarea padre con hijos, no se registra timesheet')
            return
        
        should_create = False
        
        if self.parent_id and self.parent_id.auto_log_timesheet:
            should_create = True
        elif not self.parent_id and self.auto_log_timesheet:
            should_create = True
        
        if not should_create:
            _logger.info(f'Task {self.name}: auto_log_timesheet no está activo')
            return
        
        if not self.allocated_hours or self.allocated_hours <= 0:
            _logger.info(f'Task {self.name}: no tiene horas asignadas')
            return
        
        user_to_assign = self._get_user_for_timesheet()
        
        if not user_to_assign:
            _logger.info(f'Task {self.name}: no tiene usuario asignado')
            return
        
        employee = self.env['hr.employee'].search([
            ('user_id', '=', user_to_assign.id)
        ], limit=1)
        
        if not employee:
            _logger.warning(f'Task {self.name}: el usuario {user_to_assign.name} no tiene empleado asociado')
            return
        
        existing_timesheet = self.env['account.analytic.line'].search([
            ('task_id', '=', self.id),
            ('employee_id', '=', employee.id),
            ('name', '=', f'Se completó: {self.name}')
        ], limit=1)
        
        if existing_timesheet:
            _logger.info(f'Task {self.name}: ya tiene timesheet registrado')
            return
        
        timesheet = self.env['account.analytic.line'].create({
            'name': f'Se completó: {self.name}',
            'project_id': self.project_id.id,
            'task_id': self.id,
            'employee_id': employee.id,
            'unit_amount': self.allocated_hours,
            'date': fields.Date.context_today(self),
        })
        
        _logger.info(f'Task {self.name}: timesheet creado con ID {timesheet.id} - {self.allocated_hours} horas')

    def _get_user_for_timesheet(self):
        self.ensure_one()
        
        if self.user_ids:
            return self.user_ids[0]
        
        return False