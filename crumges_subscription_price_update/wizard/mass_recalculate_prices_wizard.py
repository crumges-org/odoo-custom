from odoo import models, fields, api

class MassRecalculatePricesWizard(models.TransientModel):
    _name = 'mass.recalculate.prices.wizard'
    _description = 'Mass Recalculate Prices Wizard'

    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    line_ids = fields.One2many('mass.recalculate.prices.line.wizard', 'wizard_id', string='Price Changes')
    order_summary_ids = fields.One2many('mass.recalculate.prices.order.summary.wizard', 'wizard_id', string='Order Summary')
    
    # Totals (Header)
    current_amount_untaxed = fields.Monetary(string='Current Untaxed', compute='_compute_totals', currency_field='currency_id')
    current_amount_total = fields.Monetary(string='Current Total', compute='_compute_totals', currency_field='currency_id')
    
    new_amount_untaxed = fields.Monetary(string='New Untaxed', compute='_compute_totals', currency_field='currency_id')
    new_amount_total = fields.Monetary(string='New Total', compute='_compute_totals', currency_field='currency_id')
    
    difference_untaxed = fields.Monetary(string='Diff (Untaxed)', compute='_compute_totals', currency_field='currency_id')
    difference_total = fields.Monetary(string='Diff (Total)', compute='_compute_totals', currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency')
    show_detail = fields.Boolean(string='Show Detail', default=False)
    has_rewards = fields.Boolean(string='Has Rewards', compute='_compute_has_rewards')

    @api.model
    def default_get(self, fields_list):
        res = super(MassRecalculatePricesWizard, self).default_get(fields_list)
        if self._context.get('active_ids'):
            active_ids = self._context.get('active_ids')
            orders = self.env['sale.order'].browse(active_ids)
            
            # Validation: Filter only active subscriptions
            # We assume 'sale' state means active subscription in this context, 
            # and is_subscription must be True. We also check subscription_state to exclude churned/closed ones.
            # subscription_state '3_progress' corresponds to "In Progress" (Active).
            valid_orders = orders.filtered(lambda o: o.is_subscription and o.state == 'sale' and o.subscription_state == '3_progress')
            
            if len(valid_orders) != len(orders):
                # Option 1: Raise error if ANY invalid order is selected
                from odoo.exceptions import UserError
                raise UserError("Esta acción solo está permitida para Suscripciones Activas. Por favor, deseleccione las órdenes que no sean suscripciones o que estén cerradas/canceladas.")

                # Option 2 (Alternative): Just ignore invalid ones (Commented out)
                # active_ids = valid_orders.ids
            
            res['sale_order_ids'] = [(6, 0, valid_orders.ids)]
            res['show_detail'] = len(valid_orders) == 1
        return res

    @api.depends('sale_order_ids')
    def _compute_currency(self):
        for wizard in self:
            if wizard.sale_order_ids:
                wizard.currency_id = wizard.sale_order_ids[0].currency_id
            else:
                wizard.currency_id = False

    @api.depends('sale_order_ids')
    def _compute_has_rewards(self):
        for wizard in self:
            wizard.has_rewards = any(
                getattr(l, 'is_reward_line', False)
                for order in wizard.sale_order_ids
                for l in order.order_line
            )

    @api.depends(
        'line_ids.current_subtotal', 'line_ids.new_subtotal', 
        'order_summary_ids.current_amount_untaxed', 'order_summary_ids.new_amount_untaxed',
        'order_summary_ids.current_amount_total', 'order_summary_ids.new_amount_total'
    )
    def _compute_totals(self):
        for wizard in self:
            if wizard.show_detail:
                # In Detail view, we still focus on NET amounts for unit prices usually? 
                # But to consistent with header, we might want to sum up correctly.
                # However, line_ids currently only have new_subtotal (Net).
                # For simplicity in detail Mode (Single Order), we can trust the single order summary logic 
                # OR we can just sum up what we have. 
                # Let's rely on the order summary logic which we will implement below properly even for single order.
                # BUT wait, show_detail=True uses line_ids.
                
                # To get Total (Taxed) from lines is hard without recomputing taxes for every line in python.
                # Simplest approach: Use the single order in sale_order_ids and its current values,
                # and for NEW values, we might need a rough estimate or calculation.
                
                # Given user request, let's keep it consistent.
                # Actually, when show_detail is True, we have only ONE order.
                # We can calculate the totals from that one order's summary (which we will compute in onchange).
                
                # Let's adjust logic: Always compute order_summary_ids, even if show_detail is True?
                # Or just do the math here.
                pass
                
                # Implementation:
                wizard.current_amount_untaxed = sum(wizard.line_ids.mapped('current_subtotal'))
                # For current_amount_total in detail view, we assume it's roughly current_untaxed + tax?
                # No, better to pull from the order directly if possible.
                if len(wizard.sale_order_ids) == 1:
                     wizard.current_amount_total = wizard.sale_order_ids[0].amount_total
                     wizard.current_amount_untaxed = wizard.sale_order_ids[0].amount_untaxed
                else:
                     # Fallback
                     wizard.current_amount_total = wizard.current_amount_untaxed 
                
                # For new totals in detail view, we have new_subtotal (Net).
                wizard.new_amount_untaxed = sum(wizard.line_ids.mapped('new_subtotal'))
                
                # New Total (Taxed) is hard to guess from lines without full tax engine.
                # We will approximate it or leave it equal to untaxed if we can't easily compute.
                # OR we can iterate lines and compute taxes.
                new_taxed = 0
                previous_sections_untaxed = 0 # If we had sections
                
                # To do it right:
                if len(wizard.sale_order_ids) == 1:
                    order = wizard.sale_order_ids[0]
                    # We need to simulate tax calculation
                    # Iterate lines, get new price, compute tax.
                    # This is heavy but correct.
                    new_val = 0
                    for line_wiz in wizard.line_ids:
                        line = line_wiz.order_line_id
                        if not line: continue
                        # Compute tax
                        taxes = line.tax_id.compute_all(
                            line_wiz.new_price_with_discount, 
                            line.order_id.currency_id, 
                            line_wiz.quantity, 
                            product=line.product_id, 
                            partner=line.order_id.partner_shipping_id
                        )
                        new_val += taxes['total_included']
                    wizard.new_amount_total = new_val
                else:
                    wizard.new_amount_total = wizard.new_amount_untaxed
                    
            else:
                wizard.current_amount_untaxed = sum(wizard.order_summary_ids.mapped('current_amount_untaxed'))
                wizard.current_amount_total = sum(wizard.order_summary_ids.mapped('current_amount_total'))
                wizard.new_amount_untaxed = sum(wizard.order_summary_ids.mapped('new_amount_untaxed'))
                wizard.new_amount_total = sum(wizard.order_summary_ids.mapped('new_amount_total'))
                
            wizard.difference_untaxed = wizard.new_amount_untaxed - wizard.current_amount_untaxed
            wizard.difference_total = wizard.new_amount_total - wizard.current_amount_total

    @api.onchange('sale_order_ids')
    def _onchange_sale_order_ids(self):
        if self.show_detail:
            lines = []
            for order in self.sale_order_ids:
                normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
                
                order_updates = {}
                for line in normal_lines:
                    if line.product_id:
                        values = line._prepare_price_update_values()
                        new_gross_price = values.get('price_unit', 0)
                        new_price_with_discount = new_gross_price * (1 - values.get('discount', 0) / 100)
                        order_updates[line.id] = {'new_price': new_price_with_discount}
                
                for line in order.order_line:
                    if line.product_id:
                        current_price = line.price_unit * (1 - line.discount / 100)
                        
                        if getattr(line, 'is_reward_line', False):
                            new_gross_price = line._calculate_reward_price(order_updates) # Rewards usually return the net amount to subtract
                            discount = 0.0
                        else:
                            values = line._prepare_price_update_values()
                            new_gross_price = values.get('price_unit', 0)
                            discount = values.get('discount', 0)
                        
                        lines.append((0, 0, {
                            'order_id': order.id,
                            'order_line_id': line.id,
                            'pricelist_id': order.pricelist_id.id,
                            'product_id': line.product_id.id,
                            'current_price': line.price_unit,
                            'new_price': new_gross_price,
                            'new_price_with_discount': new_gross_price * (1 - discount / 100),
                            'quantity': line.product_uom_qty,
                            'discount': discount,
                            'discount': discount,
                            'is_reward': getattr(line, 'is_reward_line', False),
                            'is_recurring': values.get('is_recurring', False),
                            'has_recurring_pricing': values.get('has_recurring_pricing', False),
                        }))
            self.line_ids = lines
        else:
            summaries = []
            for order in self.sale_order_ids:
                current_amount_untaxed = order.amount_untaxed
                current_amount_total = order.amount_total
                
                normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
                
                order_updates = {}
                new_normal_untaxed = 0
                new_normal_total = 0
                
                for line in normal_lines:
                    if line.product_id:
                        values = line._prepare_price_update_values()
                        new_price = values.get('price_unit', 0) * (1 - values.get('discount', 0) / 100)
                        order_updates[line.id] = {'new_price': new_price}
                        new_normal_untaxed += new_price * line.product_uom_qty
                        
                        # Compute Taxed Amount for this line
                        taxes = line.tax_id.compute_all(
                            new_price, 
                            line.order_id.currency_id, 
                            line.product_uom_qty, 
                            product=line.product_id, 
                            partner=line.order_id.partner_shipping_id
                        )
                        new_normal_total += taxes['total_included']

                
                reward_lines = order.order_line.filtered(lambda l: getattr(l, 'is_reward_line', False))
                
                new_reward_untaxed = 0
                new_reward_total = 0
                
                for line in reward_lines:
                    new_reward_unit = line._calculate_reward_price(order_updates)
                    new_reward_untaxed += new_reward_unit * line.product_uom_qty
                    
                    # Compute Taxed Amount for reward
                    taxes = line.tax_id.compute_all(
                        new_reward_unit, 
                        line.order_id.currency_id, 
                        line.product_uom_qty, 
                        product=line.product_id, 
                        partner=line.order_id.partner_shipping_id
                    )
                    new_reward_total += taxes['total_included']

                
                new_amount_untaxed = new_normal_untaxed + new_reward_untaxed
                new_amount_total = new_normal_total + new_reward_total
                
                summaries.append((0, 0, {
                    'order_id': order.id,
                    'pricelist_id': order.pricelist_id.id,
                    'current_amount_untaxed': current_amount_untaxed,
                    'current_amount_total': current_amount_total,
                    'new_amount_untaxed': new_amount_untaxed,
                    'new_amount_total': new_amount_total,
                }))
            self.order_summary_ids = summaries

    def action_recalculate_prices(self):
        self.ensure_one()
        if self.sale_order_ids:
            self.sale_order_ids.action_recalculate_prices()
        return {'type': 'ir.actions.act_window_close'}


class MassRecalculatePricesLineWizard(models.TransientModel):
    _name = 'mass.recalculate.prices.line.wizard'
    _description = 'Mass Recalculate Prices Line Wizard'

    wizard_id = fields.Many2one('mass.recalculate.prices.wizard', string='Wizard', required=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', string='Order', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    current_price = fields.Monetary(string='Current Price', readonly=True, currency_field='currency_id')
    new_price = fields.Monetary(string='New Price', readonly=True, currency_field='currency_id')
    new_price_with_discount = fields.Monetary(string='New Price with Discount', readonly=True, currency_field='currency_id')
    discount = fields.Float(string='Discount (%)', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    current_subtotal = fields.Monetary(string='Current Subtotal', compute='_compute_subtotals', currency_field='currency_id')
    new_subtotal = fields.Monetary(string='New Subtotal', compute='_compute_subtotals', currency_field='currency_id')
    price_difference = fields.Monetary(string='Difference', compute='_compute_subtotals', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', string='Currency')
    is_reward = fields.Boolean(string='Is Reward', readonly=True)
    is_recurring = fields.Boolean(string='Is Recurring', readonly=True)
    has_recurring_pricing = fields.Boolean(string='Has Recurring Pricing', readonly=True)

    @api.depends('current_price', 'order_line_id.discount', 'new_price_with_discount', 'quantity')
    def _compute_subtotals(self):
        for line in self:
            current_discount = line.order_line_id.discount if line.order_line_id else 0.0
            line.current_subtotal = line.current_price * line.quantity * (1 - current_discount / 100)
            line.new_subtotal = line.new_price_with_discount * line.quantity
            line.price_difference = line.new_subtotal - line.current_subtotal


class MassRecalculatePricesOrderSummaryWizard(models.TransientModel):
    _name = 'mass.recalculate.prices.order.summary.wizard'
    _description = 'Mass Recalculate Prices Order Summary Wizard'

    wizard_id = fields.Many2one('mass.recalculate.prices.wizard', string='Wizard', required=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', string='Order', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    current_amount_untaxed = fields.Monetary(string='Current Untaxed', readonly=True, currency_field='currency_id')
    current_amount_total = fields.Monetary(string='Current Total', readonly=True, currency_field='currency_id')
    
    new_amount_untaxed = fields.Monetary(string='New Untaxed', readonly=True, currency_field='currency_id')
    new_amount_total = fields.Monetary(string='New Total', readonly=True, currency_field='currency_id')
    
    difference_untaxed = fields.Monetary(string='Diff (Untaxed)', compute='_compute_difference', currency_field='currency_id')
    difference_total = fields.Monetary(string='Diff (Total)', compute='_compute_difference', currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', string='Currency')

    @api.depends('current_amount_untaxed', 'new_amount_untaxed', 'current_amount_total', 'new_amount_total')
    def _compute_difference(self):
        for summary in self:
            summary.difference_untaxed = summary.new_amount_untaxed - summary.current_amount_untaxed
            summary.difference_total = summary.new_amount_total - summary.current_amount_total