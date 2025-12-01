from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_recalculate_prices(self):
        for order in self:
            if order.order_line:
                for line in order.order_line:
                    if line.product_id:
                        price = order.pricelist_id._get_product_price(
                            line.product_id,
                            line.product_uom_qty or 1.0,
                            partner=order.partner_id,
                            date=order.date_order,
                            uom_id=line.product_uom.id
                        )
                        line.price_unit = price
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