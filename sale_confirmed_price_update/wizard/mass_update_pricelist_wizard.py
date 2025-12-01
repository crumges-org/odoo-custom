from odoo import models, fields

class MassUpdatePricelistWizard(models.TransientModel):
    _name = 'mass.update.pricelist.wizard'
    _description = 'Mass Update Pricelist Wizard'

    pricelist_id = fields.Many2one('product.pricelist', string='New Pricelist', required=True)
    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')

    def action_update_pricelist(self):
        self.ensure_one()
        if self.sale_order_ids:
            for order in self.sale_order_ids:
                order.pricelist_id = self.pricelist_id
                for line in order.order_line:
                    if line.product_id:
                        price = self.pricelist_id._get_product_price(
                            line.product_id,
                            line.product_uom_qty or 1.0,
                            partner=order.partner_id,
                            date=order.date_order,
                            uom_id=line.product_uom.id
                        )
                        line.price_unit = price
        return {'type': 'ir.actions.act_window_close'}