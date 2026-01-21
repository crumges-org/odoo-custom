from odoo import models, fields, api

class MassRecalculatePricesWizard(models.TransientModel):
    _name = 'mass.recalculate.prices.wizard'
    _description = 'Mass Recalculate Prices Wizard'

    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    line_ids = fields.One2many('mass.recalculate.prices.line.wizard', 'wizard_id', string='Price Changes')
    order_summary_ids = fields.One2many('mass.recalculate.prices.order.summary.wizard', 'wizard_id', string='Order Summary')
    current_total = fields.Monetary(string='Current Total', compute='_compute_totals', currency_field='currency_id')
    new_total = fields.Monetary(string='New Total', compute='_compute_totals', currency_field='currency_id')
    difference = fields.Monetary(string='Difference', compute='_compute_totals', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency')
    show_detail = fields.Boolean(string='Show Detail', default=False)
    has_rewards = fields.Boolean(string='Has Rewards', compute='_compute_has_rewards')

    @api.model
    def default_get(self, fields_list):
        res = super(MassRecalculatePricesWizard, self).default_get(fields_list)
        if self._context.get('active_ids'):
            res['sale_order_ids'] = [(6, 0, self._context.get('active_ids'))]
            res['show_detail'] = len(self._context.get('active_ids')) == 1
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

    @api.depends('line_ids.current_subtotal', 'line_ids.new_subtotal', 'order_summary_ids.current_total', 'order_summary_ids.new_total')
    def _compute_totals(self):
        for wizard in self:
            if wizard.show_detail:
                wizard.current_total = sum(wizard.line_ids.mapped('current_subtotal'))
                wizard.new_total = sum(wizard.line_ids.mapped('new_subtotal'))
            else:
                wizard.current_total = sum(wizard.order_summary_ids.mapped('current_total'))
                wizard.new_total = sum(wizard.order_summary_ids.mapped('new_total'))
            wizard.difference = wizard.new_total - wizard.current_total

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
                current_total = order.amount_total
                
                normal_lines = order.order_line.filtered(lambda l: not getattr(l, 'is_reward_line', False))
                
                order_updates = {}
                new_normal_total = 0
                for line in normal_lines:
                    if line.product_id:
                        values = line._prepare_price_update_values()
                        new_price = values.get('price_unit', 0) * (1 - values.get('discount', 0) / 100)
                        order_updates[line.id] = {'new_price': new_price}
                        new_normal_total += new_price * line.product_uom_qty
                
                reward_lines = order.order_line.filtered(lambda l: getattr(l, 'is_reward_line', False))
                new_reward_total = sum(
                    line._calculate_reward_price(order_updates) * line.product_uom_qty
                    for line in reward_lines
                )
                
                new_total = new_normal_total + new_reward_total
                
                summaries.append((0, 0, {
                    'order_id': order.id,
                    'pricelist_id': order.pricelist_id.id,
                    'current_total': current_total,
                    'new_total': new_total,
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
    current_total = fields.Monetary(string='Current Total', readonly=True, currency_field='currency_id')
    new_total = fields.Monetary(string='New Total', readonly=True, currency_field='currency_id')
    difference = fields.Monetary(string='Difference', compute='_compute_difference', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', string='Currency')

    @api.depends('current_total', 'new_total')
    def _compute_difference(self):
        for summary in self:
            summary.difference = summary.new_total - summary.current_total