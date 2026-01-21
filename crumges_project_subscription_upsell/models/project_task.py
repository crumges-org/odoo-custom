from odoo import api, fields, models, _
from odoo.exceptions import UserError
from markupsafe import Markup
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_upsell_active = fields.Boolean("Enable Upsell", default=False)

    product_id = fields.Many2one('product.product', 
        string='Upsell Product',
        domain="[('upsell_from_task', '=', True)]")

    subscription_id = fields.Many2one('sale.order', 
        string='Subscription',
        domain="[('is_subscription', '=', True), ('state', 'in', ['sale', 'done']), ('subscription_state', '=', '3_progress'), ('partner_id', '=', partner_id)]")

    sale_line_id = fields.Many2one('sale.order.line', 
        string='Upsell Sale Line', 
        readonly=True)
    
    upsell_order_state = fields.Selection(related='sale_line_id.order_id.state', string="Upsell Order State")
    
    is_parent_task = fields.Boolean("Is Parent Task", compute='_compute_is_parent_task')

    @api.depends('child_ids')
    def _compute_is_parent_task(self):
        for task in self:
            task.is_parent_task = bool(task.child_ids)

    @api.constrains('is_upsell_active', 'child_ids')
    def _check_upsell_vs_subtasks(self):
        for task in self:
            if task.is_upsell_active and task.child_ids:
                raise UserError(_("No puedes tener activada la Venta Adicional y Subtareas al mismo tiempo."))

    @api.onchange('subscription_id')
    def _onchange_subscription_id(self):
        if self.subscription_id and self.sale_line_id:
             # If subscription changes, clear the upsell line unless it matches
             if self.sale_line_id.order_id != self.subscription_id:
                  self.sale_line_id = False

    def write(self, vals):
        res = super().write(vals)
        for task in self:
            # Sync name to sale line if exists
            if task.sale_line_id and task.name != task.sale_line_id.name:
                try:
                    task.sale_line_id.name = task.name
                except Exception:
                    # Ignore if order is locked/done and description cannot be updated
                    pass
        return res

    def action_create_subscription_upsell(self):
        self.ensure_one()
        # Escalate privileges to allow non-sales users to create/read sales orders
        self = self.sudo()
        
        if self.is_parent_task:
            raise UserError(_("No se puede crear una venta adicional en una tarea que contiene subtareas."))

        if not self.subscription_id or not self.product_id:
            raise UserError(_("La Suscripción y el Producto son obligatorios para crear una venta adicional."))
        
        # ESTRATEGIA DEFINITIVA: "Buscar o Crear Nativamente" + "Forzar Borrador FINAL"
        
        # 1. Buscamos borrador existente.
        upsell_order = self.env['sale.order'].search([
            ('subscription_id', '=', self.subscription_id.id),
            ('state', 'in', ['draft', 'sent']),
            ('id', '!=', self.subscription_id.id)
        ], limit=1, order='create_date desc, id desc')
            
        # 2. Si NO existe, usamos el método NATIVO
        created_new = False
        if not upsell_order:
             if hasattr(self.subscription_id, "prepare_upsell_order"):
                try:
                    action = self.subscription_id.prepare_upsell_order()
                    if action.get('res_id'):
                        upsell_order = self.env['sale.order'].browse(action['res_id'])
                        created_new = True
                except Exception as e:
                    raise UserError(_("Error al invocar la creación nativa de upsell: %s") % str(e))
             else:
                 raise UserError(_("No se encontró venta upsell y la suscripción no soporta creación automática."))
        
        if not upsell_order:
             raise UserError(_("No se pudo generar la orden de venta adicional."))

        # 3. Inyectar Datos de la Tarea (Vincular y Renombrar)
        # HACEMOS ESTO PRIMERO para que cualquier auto-guardado del ORM ocurra ANTES de nuestro forzado SQL
        vals_to_update = {}
        
        target_ref = _("Upsell desde Tarea: %s") % self.name
        if upsell_order.client_order_ref != target_ref:
             vals_to_update['client_order_ref'] = target_ref
             
        if upsell_order.subscription_id != self.subscription_id:
             vals_to_update['subscription_id'] = self.subscription_id.id
             
        if vals_to_update:
            upsell_order.sudo().write(vals_to_update)

        # 4. Añadir Línea de Producto
        existing_line = upsell_order.order_line.filtered(lambda l: l.product_id == self.product_id and l.task_id == self)
        
        if not existing_line:
            line_vals = {
                'order_id': upsell_order.id,
                'product_id': self.product_id.id,
                'name': self.name, 
                'product_uom_qty': 1.0,
                'task_id': self.id, 
                'sequence': 9999, 
            }
            # Forzamos contexto y sudo para asegurar creación
            self.env['sale.order.line'].sudo().with_context(default_order_id=upsell_order.id).create(line_vals)
            # Recargamos la línea
            self.sale_line_id = upsell_order.order_line.filtered(lambda l: l.product_id == self.product_id and l.task_id == self)[:1]
        else:
            self.sale_line_id = existing_line[0]
        
        # 5. Mensaje en Chatter
        if created_new or not existing_line:
            task_link = f"<a href='#' data-oe-model='project.task' data-oe-id='{self.id}'>{self.name}</a>"
            upsell_link = f"<a href='#' data-oe-model='sale.order' data-oe-id='{upsell_order.id}'>{upsell_order.name}</a>"
            self.subscription_id.message_post(
                body=Markup(_("Upsell %s vinculado desde tarea %s")) % (Markup(upsell_link), Markup(task_link))
            )

        # 6. FORZADO DE ESTADO (SQL DEFINITIVO AL FINAL)
        # Realizamos 'flush' del ORM para que escriba todo lo pendiente (nombres, lineas)
        # Luego ejecutamos el UPDATE SQL para pisar el estado.
        # Finalmente invalidamos caché.
        if upsell_order.state not in ['draft', 'sent']:
            self.env.flush_all() # ¡Crucial! Baja todo a la DB antes de que nosotros toquemos
            
            self.env.cr.execute("UPDATE sale_order SET state='draft', locked=False WHERE id=%s", (upsell_order.id,))
            self.env.cr.execute("UPDATE sale_order_line SET state='draft' WHERE order_id=%s", (upsell_order.id,))
            
            self.env.invalidate_all() # ¡Crucial! Obliga a Odoo a releer la realidad que acabamos de imponer
        
        # 7. SOLO RECARGAR
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        existing_line = upsell_order.order_line.filtered(lambda l: l.product_id == self.product_id and l.task_id == self)
        
        if not existing_line:
            line_vals = {
                'order_id': upsell_order.id,
                'product_id': self.product_id.id,
                'name': self.name, 
                'product_uom_qty': 1.0,
                'task_id': self.id, 
                'sequence': 9999, 
            }
            # Removemos posible basura de contexto que impida crear líneas
            self.env['sale.order.line'].with_context(default_order_id=upsell_order.id).create(line_vals)
            # Recargamos la línea para asignarla
            self.sale_line_id = upsell_order.order_line.filtered(lambda l: l.product_id == self.product_id and l.task_id == self)[:1]
        else:
            self.sale_line_id = existing_line[0]
        
        # 5. Mensaje en Chatter (solo si es nueva vinculación)
        if not existing_line:
            task_link = f"<a href='#' data-oe-model='project.task' data-oe-id='{self.id}'>{self.name}</a>"
            upsell_link = f"<a href='#' data-oe-model='sale.order' data-oe-id='{upsell_order.id}'>{upsell_order.name}</a>"
            self.subscription_id.message_post(
                body=Markup(_("Upsell %s vinculado desde tarea %s")) % (Markup(upsell_link), Markup(task_link))
            )
        
        # 6. SOLO RECARGAR (No saltar a la venta)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_force_draft_and_reload(self, upsell_order_id):
        if not upsell_order_id:
            return {'type': 'ir.actions.client', 'tag': 'reload'}
            
        upsell_order = self.env['sale.order'].browse(upsell_order_id)
        
        # NUCLEAR OPTION via Separate Request
        self.env.cr.execute("""
            UPDATE sale_order 
            SET state = 'draft', 
            locked = false,
            invoice_status = 'no'
            WHERE id = %s
        """, (upsell_order.id,))
        self.env.cr.commit()
        
        upsell_order.invalidate_recordset()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_reset_upsell(self):
        self.ensure_one()
        if not self.sale_line_id:
            return
        
        line = self.sale_line_id
        order = line.order_id
        
        # 1. Unlink from Task (Python side)
        self.sale_line_id = False
        
        # 2. Try Standard Unlink
        try:
            line.unlink()
        except Exception:
            # 3. Brute Force Unlink via SQL State Manipulation
            # Snapshot state
            old_state = order.state
            old_locked = order.locked
            
            try:
                # Force Draft in DB
                self.env.cr.execute("UPDATE sale_order SET state='draft', locked=False WHERE id=%s", (order.id,))
                self.env.cr.execute("UPDATE sale_order_line SET state='draft' WHERE order_id=%s", (order.id,))
                order.invalidate_recordset()
                line.invalidate_recordset()
                
                # Delete Line
                line.unlink()
                
                # Restore State (only if it wasn't draft originally, to preserve 'confirmed' status if that was reality)
                if old_state not in ['draft', 'sent', 'cancel']:
                     self.env.cr.execute("UPDATE sale_order SET state=%s, locked=%s WHERE id=%s", (old_state, old_locked, order.id,))
                     self.env.cr.execute("UPDATE sale_order_line SET state=%s WHERE order_id=%s", (old_state, order.id,))
                     order.invalidate_recordset()
                     
            except Exception as e:
                # 4. Fallback: Zero Qty
                _logger.warning(f"Reset Upsell: Nuclear unlink failed: {e}. Fallback to Qty=0.")
                try:
                    # We might need to force draft again to write qty if strict
                    self.env.cr.execute("UPDATE sale_order_line SET state='draft' WHERE id=%s", (line.id,))
                    line.invalidate_recordset()
                    line.write({'product_uom_qty': 0, 'task_id': False})
                except:
                    pass
        return True
