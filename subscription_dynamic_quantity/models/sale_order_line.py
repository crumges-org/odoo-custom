# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_subscription_line = fields.Boolean(
        string='Is Subscription Line',
        compute='_compute_is_subscription_line',
        store=True,
        help='Technical field to identify subscription lines',
    )
    
    has_negative_warning = fields.Boolean(
        string='Has Negative Warning',
        compute='_compute_has_negative_warning',
        help='True if subscription quantity is negative',
    )
    
    linked_service_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='id',
        compute='_compute_linked_service_lines',
        string='Linked Service Lines',
    )

    @api.depends('product_id', 'product_id.recurring_invoice')
    def _compute_is_subscription_line(self):
        for line in self:
            line.is_subscription_line = line.product_id.recurring_invoice if line.product_id else False

    @api.depends('is_subscription_line', 'product_uom_qty')
    def _compute_has_negative_warning(self):
        for line in self:
            line.has_negative_warning = (
                line.is_subscription_line and line.product_uom_qty < 0
            )

    def _compute_linked_service_lines(self):
        for line in self:
            if line.is_subscription_line and line.order_id:
                line.linked_service_line_ids = line.order_id.order_line.filtered(
                    lambda l: l.product_id.subscription_product_id == line.product_id
                )
            else:
                line.linked_service_line_ids = False

    def write(self, vals):
        """Update subscription quantities when service deliveries change."""
        res = super().write(vals)
        
        # Solo si cambió qty_delivered
        if 'qty_delivered' in vals:
            service_lines = self.filtered('product_id.subscription_product_id')
            
            for service_line in service_lines:
                if not service_line.order_id:
                    continue
                
                subscription_product = service_line.product_id.subscription_product_id
                subscription_line = service_line.order_id.order_line.filtered(
                    lambda l: l.product_id == subscription_product
                )
                
                if subscription_line:
                    new_qty = subscription_line._calculate_subscription_qty()
                    
                    if subscription_line.product_uom_qty != new_qty:
                        # Usar SQL directo para evitar recursión
                        self.env.cr.execute("""
                            UPDATE sale_order_line 
                            SET product_uom_qty = %s, write_date = NOW(), write_uid = %s
                            WHERE id = %s
                        """, (new_qty, self.env.uid, subscription_line.id))
                        
                        subscription_line.invalidate_recordset(['product_uom_qty'])
                        
                        _logger.info(
                            'Updated subscription %s: %s -> %s',
                            subscription_line.product_id.name,
                            subscription_line.product_uom_qty,
                            new_qty
                        )
        
        if 'product_id' in vals:
            for order in self.mapped('order_id'):
                order._ensure_subscription_lines()
        
        return res

    def _calculate_subscription_qty(self):
        """Calculate subscription quantity based on service lines."""
        self.ensure_one()
        
        if not self.is_subscription_line or not self.order_id:
            return 0.0
        
        service_lines = self.order_id.order_line.filtered(
            lambda l: l.product_id.subscription_product_id == self.product_id
        )
        
        if not service_lines:
            return 0.0
        
        installations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'installation'
            ).mapped('qty_delivered')
        )
        
        uninstallations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'uninstallation'
            ).mapped('qty_delivered')
        )
        
        return installations - uninstallations

    def action_recalculate_subscription_qty(self):
        """Manual recalculation button."""
        for line in self:
            if not line.is_subscription_line:
                continue
            
            new_qty = line._calculate_subscription_qty()
            
            if line.product_uom_qty != new_qty:
                line.write({'product_uom_qty': new_qty})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Updated'),
                'message': _('Subscription quantities recalculated'),
                'type': 'success',
            }
        }

    def action_view_subscription_details(self):
        """Show detailed subscription info."""
        self.ensure_one()
        
        if not self.is_subscription_line:
            return
        
        service_lines = self.order_id.order_line.filtered(
            lambda l: l.product_id.subscription_product_id == self.product_id
        )
        
        installations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'installation'
            ).mapped('qty_delivered')
        )
        
        uninstallations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'uninstallation'
            ).mapped('qty_delivered')
        )
        
        is_negative = self.product_uom_qty < 0
        
        message = _(
            '<div style="font-family: Arial, sans-serif;">'
            '<h3 style="color: #007bff;">📊 %s</h3>'
            '<table style="width: 100%%; margin: 15px 0; border-collapse: collapse;">'
            '<tr style="background: #f8f9fa;"><td style="padding: 8px; border: 1px solid #ddd;">✅ Installations</td>'
            '<td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><b>%s</b></td></tr>'
            '<tr><td style="padding: 8px; border: 1px solid #ddd;">❌ Uninstallations</td>'
            '<td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><b>%s</b></td></tr>'
            '<tr style="background: %s;"><td style="padding: 8px; border: 1px solid #ddd;"><b>Total</b></td>'
            '<td style="padding: 8px; border: 1px solid #ddd; text-align: right;">'
            '<b style="font-size: 18px; color: %s;">%s</b></td></tr>'
            '</table>%s</div>'
        ) % (
            self.product_id.name,
            installations,
            uninstallations,
            '#fff3cd' if is_negative else '#d4edda',
            '#dc3545' if is_negative else '#28a745',
            self.product_uom_qty,
            '<p style="color: #dc3545; margin-top: 10px;">⚠️ <b>Negative - Review task hours</b></p>' 
            if is_negative else ''
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Subscription Details'),
                'message': message,
                'type': 'warning' if is_negative else 'success',
                'sticky': True,
            }
        }

    @api.onchange('product_id')
    def _onchange_product_id_add_subscription(self):
        if self.product_id and self.product_id.subscription_product_id and self.order_id:
            subscription_product = self.product_id.subscription_product_id
            existing = self.order_id.order_line.filtered(
                lambda l: l.product_id == subscription_product and l.id != self.id
            )
            
            if not existing:
                return {
                    'warning': {
                        'title': _('Subscription Will Be Added'),
                        'message': _('"%s" will be added automatically') % subscription_product.name
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        
        for order in lines.mapped('order_id'):
            order._ensure_subscription_lines()
        
        return lines