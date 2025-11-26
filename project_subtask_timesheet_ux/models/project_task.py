from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    auto_log_timesheet = fields.Boolean(
        string='Registrar Horas Automáticamente',
        default=False,
    )

    def _get_root_with_switch(self):
        self.ensure_one()
        current = self
        while current.parent_id:
            if current.parent_id.auto_log_timesheet:
                return current.parent_id
            current = current.parent_id
        return current if current.auto_log_timesheet else None

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
                    task.parent_id._recalculate_parent_state()
        
        if 'allocated_hours' in vals:
            for task in self:
                if task.child_ids:
                    task._recalculate_parent_state()
                if task.parent_id:
                    task.parent_id._recalculate_parent_state()
        
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

    def unlink(self):
        parents = self.mapped('parent_id')
        res = super(ProjectTask, self).unlink()
        for parent in parents:
            if parent.exists():
                parent._recalculate_parent_state()
        return res

    def _recalculate_parent_state(self):
        self.ensure_one()
        
        if not self.child_ids:
            return
        
        direct_children = self.child_ids.filtered(lambda t: t.allocated_hours and t.allocated_hours > 0)
        
        if not direct_children:
            return
        
        completed_children = direct_children.filtered(lambda t: t.state == '1_done')
        pending_children = direct_children.filtered(lambda t: t.state != '1_done')
        
        if pending_children:
            if self.state in ['1_done', '03_approved', '02_changes_requested']:
                _logger.info(f'Task {self.name}: hay hijos directos sin completar, marcando como en progreso')
                self.write({'state': '01_in_progress'})
            return
        
        total_completed_hours = sum(child.allocated_hours for child in completed_children)
        parent_allocated_hours = self.allocated_hours or 0
        
        if total_completed_hours > parent_allocated_hours:
            if self.state != '02_changes_requested':
                _logger.info(f'Task {self.name}: horas completadas ({total_completed_hours}) exceden lo asignado ({parent_allocated_hours}), marcando como cambios solicitados')
                self.write({'state': '02_changes_requested'})
        elif total_completed_hours == parent_allocated_hours:
            if self.state != '1_done':
                _logger.info(f'Task {self.name}: horas completadas ({total_completed_hours}) coinciden con lo asignado ({parent_allocated_hours}), marcando como hecha')
                self.write({'state': '1_done'})
        else:
            if self.state != '03_approved':
                _logger.info(f'Task {self.name}: horas completadas ({total_completed_hours}) son menores a lo asignado ({parent_allocated_hours}), marcando como aprobada')
                self.write({'state': '03_approved'})

    def _reopen_parent_task(self):
        self.ensure_one()
        
        if self.state in ['1_done', '03_approved', '02_changes_requested']:
            _logger.info(f'Task {self.name}: nueva subtarea agregada, reabriendo tarea padre')
            self.write({'state': '01_in_progress'})

    def _remove_automatic_timesheet(self):
        self.ensure_one()
        
        if self.child_ids:
            _logger.info(f'Task {self.name}: tiene hijos, no se elimina timesheet')
            return
        
        root_with_switch = self._get_root_with_switch()
        
        if not root_with_switch:
            _logger.info(f'Task {self.name}: no hay ancestro con auto_log_timesheet activo, no se elimina timesheet')
            return
        
        if not self.allocated_hours or self.allocated_hours <= 0:
            _logger.info(f'Task {self.name}: no tiene horas asignadas, no se elimina timesheet')
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
            _logger.info(f'Task {self.name}: tiene hijos, no se registra timesheet')
            return
        
        root_with_switch = self._get_root_with_switch()
        
        if not root_with_switch:
            _logger.info(f'Task {self.name}: no hay ancestro con auto_log_timesheet activo')
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