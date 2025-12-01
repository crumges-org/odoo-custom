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
        
        discount = 0.0
        if pricelist_item:
            if pricelist_item.compute_price == 'percentage':
                discount = pricelist_item.percent_price
        
        return {
            'price_unit': price,
            'discount': discount,
        }

    def get_new_price_with_promotions(self):
        self.ensure_one()
        values = self._prepare_price_update_values()
        price_unit = values.get('price_unit', 0)
        discount = values.get('discount', 0)
        return price_unit * (1 - discount / 100)

    def _get_affected_product_lines(self):
        self.ensure_one()
        if not self.is_reward_line or not self.reward_id:
            return self.env['sale.order.line']
        
        reward = self.reward_id
        order = self.order_id
        
        affected_lines = self.env['sale.order.line']
        
        if hasattr(reward, 'discount_applicability'):
            if reward.discount_applicability == 'specific':
                if hasattr(reward, 'discount_product_ids') and reward.discount_product_ids:
                    affected_lines = order.order_line.filtered(
                        lambda l: not l.is_reward_line and l.product_id in reward.discount_product_ids
                    )
                elif hasattr(reward, 'discount_product_category_id') and reward.discount_product_category_id:
                    affected_lines = order.order_line.filtered(
                        lambda l: not l.is_reward_line and 
                        l.product_id.categ_id == reward.discount_product_category_id
                    )
            elif reward.discount_applicability == 'order':
                affected_lines = order.order_line.filtered(lambda l: not l.is_reward_line)
        else:
            affected_lines = order.order_line.filtered(lambda l: not l.is_reward_line)
        
        return affected_lines

    def _calculate_reward_price(self, order_updates=None):
        self.ensure_one()
        if not self.is_reward_line or not self.reward_id:
            return self.price_unit
        
        reward = self.reward_id
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