# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_subscription_lines = fields.Boolean(
        string='Has Subscription Lines',
        compute='_compute_has_subscription_lines',
        store=True,
    )
    
    has_negative_subscription = fields.Boolean(
        string='Has Negative Subscription',
        compute='_compute_has_negative_subscription',
        help='Indicates if any subscription line has negative quantity',
    )
    
    negative_subscription_message = fields.Html(
        string='Negative Subscription Warning',
        compute='_compute_has_negative_subscription',
    )
    
    @api.depends('order_line.is_subscription_line')
    def _compute_has_subscription_lines(self):
        """Check if order contains subscription lines."""
        for order in self:
            order.has_subscription_lines = any(
                line.is_subscription_line for line in order.order_line
            )

    @api.depends('order_line.is_subscription_line', 'order_line.product_uom_qty')
    def _compute_has_negative_subscription(self):
        """Check if any subscription line has negative quantity and prepare warning message."""
        for order in self:
            negative_lines = order.order_line.filtered(
                lambda l: l.is_subscription_line and l.product_uom_qty < 0
            )
            
            order.has_negative_subscription = bool(negative_lines)
            
            if negative_lines:
                # Build warning message
                warnings = []
                for line in negative_lines:
                    service_lines = order.order_line.filtered(
                        lambda l: l.product_id.subscription_product_id == line.product_id
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
                    
                    warnings.append(_(
                        '⚠️ <b>Negative Subscription:</b> %s (%s)<br/>'
                        'Installations: %s | Uninstallations: %s<br/>'
                        'Review task hours.'
                    ) % (
                        line.product_id.name,
                        line.product_uom_qty,
                        installations,
                        uninstallations
                    ))
                
                order.negative_subscription_message = '<br/>'.join(warnings)
            else:
                order.negative_subscription_message = False

    def _ensure_subscription_lines(self):
        """
        Ensure subscription lines exist for all service lines in the order.
        This method creates missing subscription lines automatically.
        """
        self.ensure_one()
        
        # Find all service lines with linked subscriptions
        service_lines = self.order_line.filtered('product_id.subscription_product_id')
        
        if not service_lines:
            return
        
        # Get unique subscription products
        subscription_products = service_lines.mapped('product_id.subscription_product_id')
        
        for subscription_product in subscription_products:
            # Check if subscription line already exists
            existing_line = self.order_line.filtered(
                lambda l: l.product_id == subscription_product
            )
            
            if not existing_line:
                # Use Command.create for proper handling in all contexts
                subscription_line_vals = {
                    'product_id': subscription_product.id,
                    'product_uom_qty': 0,
                    'product_uom': subscription_product.uom_id.id,
                    'price_unit': subscription_product.list_price,
                    'name': subscription_product.display_name,
                    'tax_id': [(6, 0, subscription_product.taxes_id.ids)],
                }
                
                # If order is saved, create directly; otherwise use Command
                if self.id:
                    subscription_line_vals['order_id'] = self.id
                    self.env['sale.order.line'].create(subscription_line_vals)
                    
                    _logger.info(
                        'Auto-created subscription line for "%s" in order %s',
                        subscription_product.name,
                        self.name
                    )
                else:
                    # For unsaved orders (onchange context), use Command
                    self.order_line = [Command.create(subscription_line_vals)]

    def action_confirm(self):
        """Override to ensure subscription lines exist before confirming."""
        for order in self:
            order._ensure_subscription_lines()
        
        return super().action_confirm()

    @api.onchange('order_line')
    def _onchange_order_line_ensure_subscriptions(self):
        """
        Automatically create subscription lines when service lines are added.
        This is triggered in the UI when the user adds/removes order lines.
        """
        if not self.order_line:
            return
        
        # Find service lines with linked subscriptions
        service_lines = self.order_line.filtered('product_id.subscription_product_id')
        
        if not service_lines:
            return
        
        # Get unique subscription products
        subscription_products = service_lines.mapped('product_id.subscription_product_id')
        
        # Check which subscriptions are missing
        for subscription_product in subscription_products:
            existing_line = self.order_line.filtered(
                lambda l: l.product_id == subscription_product
            )
            
            if not existing_line:
                # Create subscription line using Command for onchange context
                subscription_line_vals = {
                    'product_id': subscription_product.id,
                    'product_uom_qty': 0,
                    'product_uom': subscription_product.uom_id.id,
                    'price_unit': subscription_product.list_price,
                    'name': subscription_product.display_name,
                    'tax_id': [(6, 0, subscription_product.taxes_id.ids)],
                }
                
                self.order_line = [Command.create(subscription_line_vals)]
                
                _logger.info(
                    'Auto-adding subscription line for "%s" via onchange',
                    subscription_product.name
                )

    def action_recalculate_all_subscriptions(self):
        """
        Manual action to recalculate all subscription quantities in the order.
        Useful for troubleshooting or manual corrections.
        """
        self.ensure_one()
        
        subscription_lines = self.order_line.filtered('is_subscription_line')
        
        if not subscription_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Subscriptions'),
                    'message': _('This order has no subscription lines'),
                    'type': 'info',
                }
            }
        
        # Trigger recompute on all subscription lines
        subscription_lines._compute_subscription_quantity()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recalculated'),
                'message': _('%s subscription line(s) updated') % len(subscription_lines),
                'type': 'success',
            }
        }