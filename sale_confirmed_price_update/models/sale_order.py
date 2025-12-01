from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_recalculate_prices(self):
        for order in self:
            normal_lines = order.order_line.filtered(lambda l: not l.is_reward_line)
            
            order_updates = {}
            for line in normal_lines:
                if line.product_id:
                    values = line._prepare_price_update_values()
                    line.sudo().write(values)
                    order_updates[line.id] = {
                        'new_price': values['price_unit'] * (1 - values.get('discount', 0) / 100)
                    }
            
            reward_lines = order.order_line.filtered(lambda l: l.is_reward_line)
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