from odoo.tests import common
from odoo.exceptions import ValidationError

class TestTaskConstraints(common.TransactionCase):

    def setUp(self):
        super().setUp()
        try:
            self.env.cr.execute("ALTER TABLE project_project ALTER COLUMN billing_type DROP NOT NULL")
        except Exception:
            pass
        self.project_id = self.env['project.project'].create({'name': 'Test Project'})
        self.employee = self.env['hr.employee'].create({'name': 'Test Employee'})
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project_id.id,
        })

    def test_subtask_timesheet_exclusivity(self):
        """ Test that adding a subtask to a task with timesheets raises ValidationError """
        # Add timesheet
        self.env['account.analytic.line'].create({
            'name': 'Test Timesheet',
            'project_id': self.project_id.id,
            'task_id': self.task.id,
            'unit_amount': 1.0,
            'employee_id': self.employee.id,
        })
        
        # Try to add subtask
        with self.assertRaises(ValidationError):
            self.env['project.task'].create({
                'name': 'Subtask',
                'parent_id': self.task.id,
                'project_id': self.project_id.id,
            })

    def test_timesheet_subtask_exclusivity(self):
        """ Test that adding a timesheet to a task with subtasks raises ValidationError """
        # Add subtask
        self.env['project.task'].create({
            'name': 'Subtask',
            'parent_id': self.task.id,
            'project_id': self.project_id.id,
        })

        # Try to add timesheet
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].create({
                'name': 'Test Timesheet',
                'project_id': self.project_id.id,
                'task_id': self.task.id,
                'unit_amount': 1.0,
                'employee_id': self.employee.id,
            })

    def test_has_timesheets_computation(self):
        """Test that has_timesheets is computed correctly and independently of subtasks"""
        # Initially False
        self.assertFalse(self.task.has_timesheets)

        # Add timesheet to task
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Test Line',
            'project_id': self.project_id.id,
            'task_id': self.task.id,
            'unit_amount': 2,
            'employee_id': self.employee.id,
        })
        self.assertTrue(self.task.has_timesheets)

        # Remove timesheet
        timesheet.unlink()
        self.assertFalse(self.task.has_timesheets)

        # Add subtask with timesheet
        subtask = self.env['project.task'].create({
            'name': 'Subtask',
            'parent_id': self.task.id,
            'project_id': self.project_id.id,
        })
        
        self.env['account.analytic.line'].create({
            'name': 'Subtask Line',
            'project_id': self.project_id.id,
            'task_id': subtask.id,
            'unit_amount': 2,
            'employee_id': self.employee.id,
        })
        
        # Parent should NOT have timesheets, even though it has accumulated hours
        self.assertFalse(self.task.has_timesheets)
        self.assertTrue(self.task.total_hours_spent > 0)
