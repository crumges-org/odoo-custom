# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_subscription_lines = fields.Boolean(
        string='Has Subscription Lines',
        compute='_compute_has_subscription_lines',
        store=True,
    )
    
    @api.depends('order_line.is_subscription_line')
    def _compute_has_subscription_lines(self):
        for order in self:
            order.has_subscription_lines = any(
                line.is_subscription_line for line in order.order_line
            )

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
                # Use Command to add lines (works in onchange context)
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
        
        return super().action_confirm()

    @api.onchange('order_line')
    def _onchange_order_line_ensure_subscriptions(self):
        """Trigger subscription line creation when order lines change."""
        for order in self:
            order._ensure_subscription_lines()