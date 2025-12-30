from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestTaskCancellation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['project.project'].create({'name': 'Test Project'})
        self.employee = self.env['hr.employee'].create({'name': 'Test Employee'})
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user_cancel',
            'employee_ids': [(4, self.employee.id)]
        })
        
        # Create Parent Task with Automation
        self.parent_task = self.env['project.task'].create({
            'name': 'Parent Task',
            'project_id': self.project.id,
            'auto_log_timesheet': True,
        })
        
        # Create Subtask
        self.subtask = self.env['project.task'].create({
            'name': 'Subtask Auto',
            'parent_id': self.parent_task.id,
            'project_id': self.project.id,
            'allocated_hours': 10,
        })
        
        # Create Timesheet on Subtask to simulate "With Timesheets" (triggers Logic)
        self.env['account.analytic.line'].create({
            'name': f'Se completó: {self.subtask.name}',
            'task_id': self.subtask.id,
            'unit_amount': 5,
            'employee_id': self.employee.id,
            'project_id': self.project.id,
        })

    def test_cancel_parent_raises_error_and_rolls_back(self):
        """Test that canceling a parent task with auto-subtasks raises UserError and does NOT change state."""
        
        print(f"Initial State: {self.parent_task.state}")
        
        # Ensure it is NOT canceled
        self.assertNotEqual(self.parent_task.state, '1_canceled')
        
        # Try to write '1_canceled'
        with self.assertRaises(UserError) as cm:
            self.parent_task.write({'state': '1_canceled'})
        
        print(f"Caught Error: {cm.exception}")
        
        # CRITICAL: Check if state changed despite error
        self.parent_task.refresh()
        print(f"State after error: {self.parent_task.state}")
        self.assertNotEqual(self.parent_task.state, '1_canceled', "Task should NOT be canceled after UserError")
        
