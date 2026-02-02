from odoo import fields, Command
from odoo.tests.common import TransactionCase

class TestTaskSaleReport(TransactionCase):

    def test_flow(self):
        # 1. Create Product
        service_product = self.env['product.product'].create({
            'name': 'Installation Service',
            'type': 'service',
            'service_type': 'timesheet', # Creates task
            'invoice_policy': 'delivery',
            'service_tracking': 'task_global_project', # Or task_in_project
            'project_id': self.env.ref('project.project_project_1').id, # Standard project
        })

        # 2. Create SO
        so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                Command.create({
                    'product_id': service_product.id,
                    'product_uom_qty': 3.0,
                })
            ]
        })
        so.action_confirm()

        line = so.order_line[0]
        try:
            task = line.task_id
        except:
             # Depending on configuration, task might be on order or line
             task = self.env['project.task'].search([('sale_line_id', '=', line.id)], limit=1)
        
        if not task:
            # Fallback if no task created (config dependent), create manually linked
            task = self.env['project.task'].create({
                'name': 'Task for SO',
                'sale_line_id': line.id,
                'project_id': service_product.project_id.id
            })

        print(f"Parent Task: {task.name} ({task.id}) - Sale Line: {task.sale_line_id.id}")

        # 3. Create Subtask
        subtask = self.env['project.task'].create({
            'name': 'Subtask 1',
            'parent_id': task.id,
            'project_id': task.project_id.id,
        })
        
        # Verify Visibility Logic (simulation)
        # Check if subtask has sale_order_id
        print(f"Subtask Sale Order: {subtask.sale_order_id}")
        
        # 4. Set values and Close
        subtask.write({
            'sale_report_qty': 1.0,
            'sale_report_info': 'TEST-123'
        })
        
        # Correctly find a folded stage
        done_stage = self.env['project.task.type'].search([('fold', '=', True)], limit=1)
        if not done_stage:
            done_stage = self.env['project.task.type'].create({'name': 'Done', 'fold': True})
            
        subtask.write({'stage_id': done_stage.id})
        
        # 5. Check Result
        print(f"Delivered Qty: {line.qty_delivered}")
        if line.qty_delivered != 1.0:
            print("FAILURE: Delivered Qty not updated.")
        else:
            print("SUCCESS: Delivered Qty updated.")
            
        # Check Notes
        note_lines = so.order_line.filtered(lambda l: l.display_type == 'line_note')
        print(f"Notes Found: {len(note_lines)}")
        for n in note_lines:
             print(f"Note: {n.name}")

