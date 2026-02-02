from odoo import models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_price_update_values(self):
        self.ensure_one()
        order = self.order_id
        product = self.product_id
        
        price = order.pricelist_id._get_product_price(
            product,
            self.product_uom_qty or 1.0,
            partner=order.partner_id,
            date=order.date_order,
            uom_id=self.product_uom.id
        )
        
        pricelist_item = order.pricelist_id._get_product_rule(
            product,
            self.product_uom_qty or 1.0,
            uom=self.product_uom,
            date=order.date_order
        )

        # Logic for recurring products (Subscriptions)
        is_recurring = getattr(product, 'recurring_invoice', False)
        has_recurring_pricing = False
        
        # Check if sale_subscription logic applies
        if is_recurring and getattr(order, 'plan_id', False):
            # Try to get recurring pricing
            pricing = False
            if hasattr(product, '_get_pricing'):
                pricing = product._get_pricing(product, order.pricelist_id, order.plan_id.id)
            elif 'sale.subscription.pricing' in self.env:
                 pricing = self.env['sale.subscription.pricing'].sudo()._get_first_suitable_recurring_pricing(
                    product, plan=order.plan_id, pricelist=order.pricelist_id
                )
            
            if pricing:
                price = pricing.currency_id._convert(
                    pricing.price, 
                    order.currency_id, 
                    order.company_id, 
                    order.date_order or fields.Date.today()
                )
                has_recurring_pricing = True
                # Recurring prices usually don't use the standard pricelist discounts in the same way, 
                # or the price fetched is already the final recurring price.
                # However, we still check pricelist item for discount if we didn't find specific recurring pricing?
                # No, if we found pricing, we use that price.
                # If we didn't find pricing, we fall back to standard price (already calculated above).

        discount = self.discount
        if pricelist_item and not has_recurring_pricing:
            rule = self.env['product.pricelist.item'].browse(pricelist_item)
            if rule.compute_price == 'percentage':
                discount = rule.percent_price
                if discount != 100:
                    price = price / (1 - discount / 100)
        
        return {
            'price_unit': price,
            'discount': discount,
            'is_recurring': is_recurring,
            'has_recurring_pricing': has_recurring_pricing,
        }

    def get_new_price_with_promotions(self):
        self.ensure_one()
        values = self._prepare_price_update_values()
        price_unit = values.get('price_unit', 0)
        discount = values.get('discount', 0)
        return price_unit * (1 - discount / 100)

    def _get_affected_product_lines(self):
        self.ensure_one()
        if not getattr(self, 'is_reward_line', False) or not getattr(self, 'reward_id', False):
            return self.env['sale.order.line']
        
        reward = getattr(self, 'reward_id', False)
        order = self.order_id
        
        affected_lines = self.env['sale.order.line']
        
        if hasattr(reward, 'discount_applicability'):
            if reward.discount_applicability == 'specific':
                if hasattr(reward, 'discount_product_ids') and reward.discount_product_ids:
                    affected_lines = order.order_line.filtered(
                        lambda l: not getattr(l, 'is_reward_line', False) and l.product_id in reward.discount_product_ids
                    )
                elif hasattr(reward, 'discount_product_category_id') and reward.discount_product_category_id:
                    affected_lines = order.order_line.filtered(
                        lambda l: not getattr(l, 'is_reward_line', False) and 
                        l.product_id.categ_id == reward.discount_product_category_id
                    )
            elif reward.discount_applicability == 'order':
                affected_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
        else:
            affected_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
        
        return affected_lines

    def _calculate_reward_price(self, order_updates=None):
        self.ensure_one()
        if not getattr(self, 'is_reward_line', False) or not getattr(self, 'reward_id', False):
            return self.price_unit
        
        reward = getattr(self, 'reward_id', False)
        order = self.order_id
        
        if reward.reward_type == 'discount':
            affected_lines = self._get_affected_product_lines()
            
            if order_updates:
                affected_total = sum(
                    order_updates.get(line.id, {}).get('new_price', line.price_unit * (1 - line.discount / 100)) * line.product_uom_qty
                    for line in affected_lines
                )
            else:
                affected_total = sum(
                    line.price_unit * (1 - line.discount / 100) * line.product_uom_qty
                    for line in affected_lines
                )
            
            if reward.discount_mode == 'percent':
                discount_amount = affected_total * (reward.discount / 100)
                return -discount_amount
            elif reward.discount_mode == 'per_order':
                return -reward.discount
            elif reward.discount_mode == 'per_point':
                points = order._get_reward_points() if hasattr(order, '_get_reward_points') else 0
                discount_amount = points * reward.discount
                return -discount_amount
                
        elif reward.reward_type == 'product':
            if reward.reward_product_id:
                price = order.pricelist_id._get_product_price(
                    reward.reward_product_id,
                    self.product_uom_qty or 1.0,
                    partner=order.partner_id,
                    date=order.date_order,
                    uom_id=self.product_uom.id
                )
                discount_amount = price * (reward.discount_product_price / 100) if reward.discount_product_price else price
                return -discount_amount
        
        return self.price_unit