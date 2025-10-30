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
        help='Technical field to identify subscription lines managed by this module',
    )
    
    has_negative_warning = fields.Boolean(
        string='Has Negative Warning',
        compute='_compute_subscription_quantity',
        store=True,
        help='Indicates if this line would have negative quantity without protection',
    )
    
    linked_service_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='id',
        compute='_compute_linked_service_lines',
        string='Linked Service Lines',
        help='Service lines (installations/uninstallations) that affect this subscription quantity',
    )

    @api.depends('product_id', 'product_id.recurring_invoice')
    def _compute_is_subscription_line(self):
        """Identify subscription lines automatically."""
        for line in self:
            line.is_subscription_line = bool(
                line.product_id and line.product_id.recurring_invoice
            )

    def _compute_linked_service_lines(self):
        """Find all service lines that affect this subscription."""
        for line in self:
            if line.is_subscription_line and line.order_id:
                line.linked_service_line_ids = line.order_id.order_line.filtered(
                    lambda l: l.product_id.subscription_product_id == line.product_id
                )
            else:
                line.linked_service_line_ids = False

    @api.depends(
        'is_subscription_line',
        'order_id.order_line.qty_delivered',
        'order_id.order_line.product_id.subscription_product_id',
        'order_id.order_line.product_id.subscription_service_type',
    )
    def _compute_subscription_quantity(self):
        """
        Automatically calculate subscription quantity based on delivered services.
        This compute field triggers whenever related service lines change.
        """
        for line in self:
            if not line.is_subscription_line or not line.order_id:
                line.has_negative_warning = False
                continue
            
            # Find all service lines for this subscription
            service_lines = line.order_id.order_line.filtered(
                lambda l: l.product_id.subscription_product_id == line.product_id
            )
            
            if not service_lines:
                line.has_negative_warning = False
                continue
            
            # Calculate quantities
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
            
            calculated_qty = installations - uninstallations
            
            # Set warning flag if negative
            line.has_negative_warning = calculated_qty < 0
            
            # Update quantity if different (prevents infinite loops)
            if line.product_uom_qty != calculated_qty:
                # Use SQL to avoid triggering computes recursively
                try:
                    self.env.cr.execute("""
                        UPDATE sale_order_line 
                        SET product_uom_qty = %s, 
                            write_date = NOW(), 
                            write_uid = %s
                        WHERE id = %s
                    """, (calculated_qty, self.env.uid, line.id))
                    
                    # Invalidate cache for this record
                    line.invalidate_recordset(['product_uom_qty'])
                    
                    _logger.info(
                        'Auto-updated subscription %s (ID: %s): qty %s -> %s',
                        line.product_id.name,
                        line.id,
                        line.product_uom_qty,
                        calculated_qty
                    )
                except Exception as e:
                    _logger.warning(
                        'Failed to auto-update subscription qty for line %s: %s',
                        line.id, str(e)
                    )

    def write(self, vals):
        """
        Override write to trigger subscription recalculation when service deliveries change.
        """
        res = super().write(vals)
        
        # If qty_delivered changed on service lines, recalculate affected subscriptions
        if 'qty_delivered' in vals:
            service_lines = self.filtered('product_id.subscription_product_id')
            
            for service_line in service_lines:
                if not service_line.order_id:
                    continue
                
                subscription_product = service_line.product_id.subscription_product_id
                subscription_lines = service_line.order_id.order_line.filtered(
                    lambda l: l.product_id == subscription_product and l.is_subscription_line
                )
                
                # Trigger recompute
                if subscription_lines:
                    subscription_lines._compute_subscription_quantity()
        
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure subscription lines exist when creating service lines."""
        lines = super().create(vals_list)
        
        # Group by order to avoid multiple calls
        for order in lines.mapped('order_id'):
            order._ensure_subscription_lines()
        
        return lines

    def action_recalculate_subscription_qty(self):
        """Manual recalculation action (button in UI)."""
        subscription_lines = self.filtered('is_subscription_line')
        
        if not subscription_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Subscription Lines'),
                    'message': _('Please select subscription lines to recalculate'),
                    'type': 'warning',
                }
            }
        
        # Trigger recompute
        subscription_lines._compute_subscription_quantity()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recalculated'),
                'message': _('Subscription quantities have been updated'),
                'type': 'success',
            }
        }

    def action_view_subscription_details(self):
        """Show detailed subscription calculation breakdown."""
        self.ensure_one()
        
        if not self.is_subscription_line:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Not a Subscription'),
                    'message': _('This line is not a subscription product'),
                    'type': 'warning',
                }
            }
        
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
        
        calculated_qty = installations - uninstallations
        is_negative = calculated_qty < 0
        
        # Build detailed HTML message
        message = _(
            '<div style="font-family: Arial, sans-serif;">'
            '<h3 style="color: #007bff;">📊 Subscription Details: %s</h3>'
            '<table style="width: 100%%; border-collapse: collapse; margin: 15px 0;">'
            '<tr style="background-color: #f8f9fa;">'
            '<th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Metric</th>'
            '<th style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">Value</th>'
            '</tr>'
            '<tr><td style="padding: 10px; border: 1px solid #dee2e6;">✅ Installations Delivered</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr style="background-color: #f8f9fa;"><td style="padding: 10px; border: 1px solid #dee2e6;">❌ Uninstallations Delivered</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr><td style="padding: 10px; border: 1px solid #dee2e6;">➖ Calculated Quantity</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr style="background-color: %s;">'
            '<td style="padding: 10px; border: 1px solid #dee2e6;"><strong>🔒 Final Quantity</strong></td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">'
            '<strong style="font-size: 18px; color: %s;">%s</strong></td></tr>'
            '</table>'
            '%s'
            '</div>'
        ) % (
            self.product_id.name,
            installations,
            uninstallations,
            calculated_qty,
            '#fff3cd' if is_negative else '#d4edda',
            '#dc3545' if is_negative else '#28a745',
            self.product_uom_qty,
            '<div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 15px;">'
            '<h4 style="margin-top: 0; color: #856404;">⚠️ Negative Quantity</h4>'
            '<p style="margin-bottom: 0;">Review task hours - uninstallations exceed installations.</p></div>'
            if is_negative else ''
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Subscription Information'),
                'message': message,
                'type': 'warning' if is_negative else 'success',
                'sticky': True,
            }
        }

    @api.onchange('product_id')
    def _onchange_product_id_subscription_warning(self):
        """Show warning when adding a service product with linked subscription."""
        if self.product_id and self.product_id.subscription_product_id and self.order_id:
            subscription_product = self.product_id.subscription_product_id
            
            # Check if subscription already exists
            existing = self.order_id.order_line.filtered(
                lambda l: l.product_id == subscription_product and l.id != self.id
            )
            
            if not existing:
                return {
                    'warning': {
                        'title': _('Subscription Product Will Be Added'),
                        'message': _(
                            'A subscription line for "%s" will be automatically added to this order. '
                            'The quantity will be calculated based on delivered installations/uninstallations.'
                        ) % subscription_product.name
                    }
                }
