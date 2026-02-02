from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_price_difference = fields.Boolean(compute='_compute_has_price_difference', search='_search_has_price_difference')

    def _search_has_price_difference(self, operator, value):
        if operator not in ['=', '!=']:
            raise ValueError('This operator is not supported')
        
        # We only care if we are searching for True
        # If searching for False, we invert the logic roughly, but typically standard search is for "Has Difference"
        
        target = True
        if (operator == '=' and value is False) or (operator == '!=' and value is True):
            target = False
            
        # Optimization: First filter candidates by SQL domain
        # Candidates: Active Subscriptions
        domain = [('is_subscription', '=', True), ('state', '=', 'sale'), ('subscription_state', '=', '3_progress')]
        candidates = self.search(domain)
        
        matching_ids = []
        for order in candidates:
            # We must verify the difference. We can reuse the compute logic or extract it.
            # To avoid messing up current logic, let's reuse a helper or just recalculate.
            # Since _compute works on recordset, we can wrap it or duplicate core logic.
            # Duplicating core logic is safer to avoid side effects of triggers.
            
            has_diff = False
            normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
            order_updates = {}
            
            for line in normal_lines:
                if line.product_id:
                    values = line._prepare_price_update_values()
                    new_gross_price = values.get('price_unit', 0)
                    new_price = new_gross_price * (1 - values.get('discount', 0) / 100)
                    current_price = line.price_unit * (1 - line.discount / 100)
                    
                    if abs(new_price - current_price) > 0.01:
                        has_diff = True
                        break
                    order_updates[line.id] = {'new_price': new_price}
            
            if not has_diff:
                 reward_lines = order.order_line.filtered(lambda l: getattr(l, 'is_reward_line', False))
                 for line in reward_lines:
                     new_reward_price = line._calculate_reward_price(order_updates)
                     if abs(new_reward_price - line.price_unit) > 0.01:
                         has_diff = True
                         break
            
            if has_diff == target:
                matching_ids.append(order.id)
                
        return [('id', 'in', matching_ids)]

    def _compute_has_price_difference(self):
        for order in self:
            has_diff = False
            # Only compute for active subscriptions to save performance
            # Using 'is_subscription' as per previous fixes (not is_recurring)
            is_sub = getattr(order, 'is_subscription', False)
            if is_sub and order.state == 'sale' and getattr(order, 'subscription_state', '') == '3_progress':
                # Check normal lines
                normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
                order_updates = {}
                
                for line in normal_lines:
                    if line.product_id:
                        values = line._prepare_price_update_values()
                        new_gross_price = values.get('price_unit', 0)
                        current_gross_price = values.get('current_price_unit', line.price_unit) # fallback to line.price_unit if not returned
                        
                        # We compare net prices or gross? Usually net price with discount change is what matters.
                        # Logic from wizard:
                        # new_price = values['price_unit'] * (1 - values.get('discount', 0) / 100)
                        # current_price = line.price_unit * (1 - line.discount / 100)
                        
                        new_price = new_gross_price * (1 - values.get('discount', 0) / 100)
                        current_price = line.price_unit * (1 - line.discount / 100)
                        
                        # Use float_compare for robustness
                        if abs(new_price - current_price) > 0.01: # simple tolerance
                            has_diff = True
                            break
                        
                        order_updates[line.id] = {'new_price': new_price}
                
                if not has_diff:
                    # Check reward lines if normal lines didn't trigger diff
                    reward_lines = order.order_line.filtered(lambda l: getattr(l, 'is_reward_line', False))
                    for line in reward_lines:
                        new_reward_price = line._calculate_reward_price(order_updates)
                        if abs(new_reward_price - line.price_unit) > 0.01:
                            has_diff = True
                            break
            
            order.has_price_difference = has_diff

    def action_recalculate_prices(self):
        for order in self:
            normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
            
            order_updates = {}
            for line in normal_lines:
                if line.product_id:
                    values = line._prepare_price_update_values()
                    # Remove non-writable fields used for wizard display
                    values.pop('is_recurring', None)
                    values.pop('has_recurring_pricing', None)
                    line.sudo().write(values)
                    order_updates[line.id] = {
                        'new_price': values['price_unit'] * (1 - values.get('discount', 0) / 100)
                    }
            
            reward_lines = order.order_line.filtered(lambda l: getattr(l, 'is_reward_line', False))
            for reward_line in reward_lines:
                new_reward_price = reward_line._calculate_reward_price(order_updates)
                reward_line.sudo().write({'price_unit': new_reward_price})
        
        return True

    def action_open_recalculate_prices_wizard(self):
        return {
            'name': 'Recalculate Prices',
            'type': 'ir.actions.act_window',
            'res_model': 'mass.recalculate.prices.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_ids': self.ids}
        }