# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _


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
        for order in self:
            order.has_subscription_lines = any(
                line.is_subscription_line for line in order.order_line
            )

    @api.depends('order_line.is_subscription_line', 
                 'order_line.calculated_subscription_qty',
                 'order_line.has_negative_warning')
    def _compute_has_negative_subscription(self):
        """Check if any subscription line has negative quantity."""
        for order in self:
            negative_lines = order.order_line.filtered(
                lambda l: l.is_subscription_line and l.calculated_subscription_qty < 0
            )
            
            order.has_negative_subscription = bool(negative_lines)
            
            if negative_lines:
                products_list = ', '.join([
                    f'{line.product_id.name} ({line.calculated_subscription_qty})' 
                    for line in negative_lines
                ])
                
                order.negative_subscription_message = _(
                    '⚠️ <strong>Negative Subscription:</strong> %s<br/>'
                    'Review task hours - uninstallations exceed installations.'
                ) % products_list
            else:
                order.negative_subscription_message = False

    def _ensure_subscription_lines(self):
        """
        Ensure that for each unique subscription product referenced by service lines,
        there is a corresponding subscription line in the order.
        """
        self.ensure_one()
        
        service_lines = self.order_line.filtered('product_id.subscription_product_id')
        
        subscription_products = service_lines.mapped('product_id.subscription_product_id')
        
        for subscription_product in subscription_products:
            existing_line = self.order_line.filtered(
                lambda l: l.product_id == subscription_product
            )
            
            if not existing_line:
                self.order_line = [Command.create({
                    'product_id': subscription_product.id,
                    'product_uom_qty': 0,
                    'product_uom': subscription_product.uom_id.id,
                    'price_unit': subscription_product.list_price,
                    'name': subscription_product.name,
                })]

    def action_confirm(self):
        """Ensure subscription lines exist before confirming the order."""
        for order in self:
            order._ensure_subscription_lines()
            # Sincronizar cantidades antes de confirmar
            subscription_lines = order.order_line.filtered('is_subscription_line')
            if subscription_lines:
                subscription_lines.action_sync_subscription_qty()
        
        return super().action_confirm()

    @api.onchange('order_line')
    def _onchange_order_line_ensure_subscriptions(self):
        """Trigger subscription line creation when order lines change."""
        for order in self:
            order._ensure_subscription_lines()

    def action_sync_all_subscriptions(self):
        """Sync all subscription lines in this order."""
        self.ensure_one()
        
        subscription_lines = self.order_line.filtered('is_subscription_line')
        
        if not subscription_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Subscriptions'),
                    'message': _('This order has no subscription lines to synchronize.'),
                    'type': 'info',
                }
            }
        
        # Sincronizar todas las líneas
        subscription_lines.action_sync_subscription_qty()
        
        # Contar cuántas se actualizaron
        synced_count = len(subscription_lines)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Subscriptions Synchronized'),
                'message': _('%s subscription line(s) updated successfully.') % synced_count,
                'type': 'success',
            }
        }