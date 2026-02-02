from odoo import fields, Command
from odoo.tests.common import TransactionCase

class TestDebugMilestone(TransactionCase):

    def test_relations(self):
        # 1. Create Product with Milestone Policy
        product = self.env['product.product'].create({
            'name': 'Servicio Hitos',
            'type': 'service',
            'service_type': 'milestones', # This is usually 'manual' or special in standard?
                                          # In Odoo 16+, 'milestones' relies on 'service_policy'='delivered_milestones'
            'invoice_policy': 'delivery',
            'service_policy': 'delivered_milestones',
            'service_tracking': 'task_global_project',
            'project_id': self.env.ref('project.project_project_1').id,
        })
        
        print(f"Product Created: {product.name} - Policy: {product.service_policy}")

        # 2. Create SO
        so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                Command.create({
                    'product_id': product.id,
                    'product_uom_qty': 1.0,
                })
            ]
        })
        so.action_confirm()
        print(f"SO Confirmed: {so.name}")
        
        line = so.order_line[0]
        print(f"SO Line ID: {line.id}")
        
        # 3. Check Task
        task = line.task_id
        if not task:
             # Search if linked via sale_line_id
             task = self.env['project.task'].search([('sale_line_id', '=', line.id)], limit=1)
             
        if task:
            print(f"Task Found: {task.name} (ID: {task.id})")
            print(f"Task Sale Line: {task.sale_line_id.id}")
        else:
            print("NO TASK FOUND LINKED TO LINE.")
            # Standard Odoo should create task if service_tracking is set.
            
        # 4. Check Milestone
        # User says "automatically triggers a milestone".
        # Let's search for milestones linked to this line or order.
        milestones = self.env['project.milestone'].search([('sale_line_id', '=', line.id)])
        print(f"Milestones linked to Line: {len(milestones)}")
        for m in milestones:
            print(f" - Milestone: {m.name} (ID: {m.id}, Reached: {m.is_reached}, Pct: {m.quantity_percentage})")
            
        milestones_order = self.env['project.milestone'].search([('sale_line_id.order_id', '=', so.id)])
        print(f"Milestones linked to Order (via any line): {len(milestones_order)}")

        # 5. Simulate Code Logic
        if task:
            print("--- Simulating Logic ---")
            pertinent_sale_line = task.sale_line_id or task.parent_id.sale_line_id
            print(f"Pertinent Line: {pertinent_sale_line}")
            
            # Search logic used in code
            found = self.env['project.milestone'].search([('sale_line_id', '=', pertinent_sale_line.id)], limit=1)
            print(f"Search Code Result: {found}")

