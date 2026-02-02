from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import pytz

class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_report_note_line_id = fields.Many2one('sale.order.line', string='Report Note Line', copy=False)
    is_sale_reported = fields.Boolean(string='Is Reported to Sale', default=False, copy=False)
    
    # Internal field to help tracking, though we rely on dynamic calc mostly now.
    sale_reported_qty = fields.Float(string='Qty Reported', copy=False)

    sale_report_delivery_automation = fields.Boolean(related='sale_line_id.product_id.sale_report_delivery_automation', string="Automatización Activa", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            parent_id = vals.get('parent_id')
            if parent_id:
                parent = self.browse(parent_id)
                # Check automation logic to apply constraints
                # If product is NOT automated, standard behavior allows depth?
                # User Requirement: "any other task... behaves normally".
                # So we check parent's product automation flag.
                # Assuming parent.sale_line_id is set or we trace it.
                
                is_automated = False
                pertinent_line = parent._get_pertinent_sale_line()
                if pertinent_line and pertinent_line.product_id.sale_report_delivery_automation:
                    is_automated = True
                
                if is_automated:
                    # Constraint 1: Max 1 Level
                    if parent.parent_id:
                         raise ValidationError(_("No puedes crear subtareas de subtareas en un servicio automatizado."))
                    # Constraint 2: Lock Creation
                    siblings_done = self.search_count([
                        ('parent_id', '=', parent_id),
                        ('is_sale_reported', '=', True)
                    ])
                    if siblings_done > 0:
                        raise ValidationError(_("No puedes agregar más subtareas porque ya se ha reportado avance."))
        return super().create(vals_list)

    def write(self, vals):
        # Constraint: Prevent Manual Parent State Change if Automated and has Children
        if 'stage_id' in vals or 'state' in vals:
            for task in self:
                if task.child_ids and task._is_automation_active():
                    # Allow system updates (bypass context could be used, but for now we block specific UI changes)
                    # How to distinguish System call (auto-close) vs User Call?
                    # The auto-close calls self.parent_id.write().
                    # We can use context 'automation_running'.
                    if not self.env.context.get('automation_running'):
                         raise UserError(_("No puedes cambiar manualmente el estado de una tarea padre automatizada. Su estado depende de las subtareas."))

        res = super().write(vals)
        if 'stage_id' in vals or 'state' in vals:
            self._check_sale_report_trigger()
        return res

    def _is_automation_active(self):
        pertinent_line = self._get_pertinent_sale_line()
        return pertinent_line and pertinent_line.product_id.sale_report_delivery_automation

    def _check_sale_report_trigger(self):
        for task in self:
            pertinent_sale_line = task._get_pertinent_sale_line()
            if not pertinent_sale_line:
                continue

            # LOGIC GATE: Only run if Product Flag is True
            if not pertinent_sale_line.product_id.sale_report_delivery_automation:
                continue

            # Determine State
            # Check both stage.fold and state field if available
            is_closed = task.stage_id.fold or getattr(task, 'state', '') in ['1_done', '1_canceled', 'done']
            
            # Action logic
            if is_closed and not task.is_sale_reported:
                 task._action_mark_done(pertinent_sale_line)
                 task._update_milestone_progress(pertinent_sale_line)
                 task._check_parent_auto_close() # Check if parent should close
            elif not is_closed and task.is_sale_reported:
                 task._action_mark_undone(pertinent_sale_line)
                 task._update_milestone_progress(pertinent_sale_line)
                 # Reverting doesn't reopen parent usually (user choice)

    def _get_pertinent_sale_line(self):
        self.ensure_one()
        # 1. Direct Link
        if self.sale_line_id:
            return self.sale_line_id
        if self.parent_id and self.parent_id.sale_line_id:
            return self.parent_id.sale_line_id
            
        # 2. Fallback via Project Milestones
        if self.project_id:
            milestone = self.env['project.milestone'].search([
                ('project_id', '=', self.project_id.id),
                ('sale_line_id', '!=', False)
            ], limit=1)
            if milestone:
                return milestone.sale_line_id
        return False
        
    def _check_parent_auto_close(self):
        """
        If all siblings (including me) are Done, mark Parent as Done.
        """
        self.ensure_one()
        if not self.parent_id:
            return
            
        siblings = self.parent_id.child_ids
        all_reported = all(t.is_sale_reported for t in siblings)
        
        if all_reported:
             # V6: Only update STATE to '1_done', do NOT change stage (fold).
             # Use Context to bypass the write constraint we just added.
             self.parent_id.with_context(automation_running=True).write({'state': '1_done'})

    def _action_mark_done(self, sale_line):
        self.ensure_one()
        # Create Note ONLY if I have no children (V6)
        if not self.child_ids:
            self._create_so_report_note(sale_line.order_id, self.name)
        self.write({'is_sale_reported': True})

    def _action_mark_undone(self, sale_line):
        self.ensure_one()
        # Remove Note
        if self.sale_report_note_line_id:
            try:
                self.sale_report_note_line_id.sudo().unlink()
            except:
                pass
        self.write({'is_sale_reported': False})
        
        # Cleanup Section
        if sale_line:
             self._clean_so_section(sale_line.order_id)

    def _update_milestone_progress(self, sale_line):
        self.ensure_one()
        
        # 1. Scope
        if self.parent_id:
            all_tasks = self.parent_id.child_ids
        else:
            all_tasks = self
            if self.child_ids:
                all_tasks = self.child_ids
            
        # Ensure collection
        if not isinstance(all_tasks, models.Model):
             all_tasks = self
             
        total_count = len(all_tasks)
        if total_count == 0:
            return

        done_count = 0
        for t in all_tasks:
            # Check reported flag
            if t.is_sale_reported:
                done_count += 1
        
        ratio = done_count / total_count
        
        # 3. Find Milestone
        milestones = self.env['project.milestone'].search([
            ('sale_line_id', '=', sale_line.id)
        ], limit=1)
        
        if not milestones:
            return

        milestone = milestones[0]
        
        # Reached if > 0? Or Reached if 100%?
        # User Feedback: "deberia decir 50 por ciento y estar el objetivo en 'Alcanzado'".
        # So "Partial Progress" = Reached.
        vals = {
            'quantity_percentage': ratio,
            'is_reached': ratio > 0
        }
        
        try:
             milestone.sudo().write(vals)
        except Exception as e:
              pass 

    def _create_so_report_note(self, order, name):
        # Ensure Section
        section_name = "Información de trabajos realizados"
        lines = order.order_line
        section = lines.filtered(lambda l: l.display_type == 'line_section' and l.name == section_name)
        
        last_sequence = 0
        if lines:
            last_sequence = max(lines.mapped('sequence'))

        if not section:
            self.env['sale.order.line'].sudo().create({
                'order_id': order.id,
                'display_type': 'line_section',
                'name': section_name,
                'sequence': last_sequence + 1,
            })
            last_sequence += 1
            
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        now = datetime.now(tz).strftime('%d/%m/%Y %H:%M')
        
        note_content = f"{name} -> Hecho ({now})"
        
        note_line = self.env['sale.order.line'].sudo().create({
            'order_id': order.id,
            'display_type': 'line_note',
            'name': note_content,
            'sequence': last_sequence + 2, 
        })
        self.sale_report_note_line_id = note_line.id

    def _clean_so_section(self, order):
        line_ids = order.order_line.ids
        count = self.env['project.task'].sudo().search_count([
            '|',
            '&', ('sale_line_id', 'in', line_ids), ('is_sale_reported', '=', True),
            '&', ('parent_id.sale_line_id', 'in', line_ids), ('is_sale_reported', '=', True)
        ])
        
        if count == 0:
             section_name = "Información de trabajos realizados"
             section = order.order_line.filtered(lambda l: l.display_type == 'line_section' and l.name == section_name)
             if section:
                 try:
                     section.sudo().unlink()
                 except:
                     pass
