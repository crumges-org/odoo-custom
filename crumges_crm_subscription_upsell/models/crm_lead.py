from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crumges_upsell_subscription_ids = fields.Many2many(
        'sale.order',
        compute='_compute_crumges_upsell_subscription_ids',
        string='Active Subscriptions',
        help="Active subscriptions linked to the customer of this opportunity."
    )

    crumges_pending_upsell_ids = fields.Many2many(
        'sale.order',
        compute='_compute_crumges_pending_upsell_ids',
        string='Pending Upsells',
        help="Pending upsell orders (quotations) linked to the customer of this opportunity."
    )

    has_active_subscriptions = fields.Boolean(compute='_compute_has_active_subscriptions')
    has_pending_upsells = fields.Boolean(compute='_compute_has_pending_upsells')
    
    @api.depends('crumges_upsell_subscription_ids')
    def _compute_has_active_subscriptions(self):
        for lead in self:
            lead.has_active_subscriptions = bool(lead.crumges_upsell_subscription_ids)

    @api.depends('crumges_pending_upsell_ids')
    def _compute_has_pending_upsells(self):
        for lead in self:
            lead.has_pending_upsells = bool(lead.crumges_pending_upsell_ids)

    @api.depends('partner_id')
    def _compute_crumges_upsell_subscription_ids(self):
        for lead in self:
            if not lead.partner_id:
                lead.crumges_upsell_subscription_ids = False
                continue
            
            # Find subscriptions for the partner or its parent/children
            partners = lead.partner_id
            if lead.partner_id.parent_id:
                partners |= lead.partner_id.parent_id
            if lead.partner_id.child_ids:
                partners |= lead.partner_id.child_ids
            
            # Search for active subscriptions
            # Criteria: is_subscription=True, state in [sale, done], internal subscription state = 3_progress (In Progress)
            subscriptions = self.env['sale.order'].search([
                ('partner_id', 'in', partners.ids),
                ('is_subscription', '=', True),
                ('state', 'in', ['sale', 'done']),
                ('subscription_state', '=', '3_progress')
            ])
            lead.crumges_upsell_subscription_ids = subscriptions

    @api.depends('partner_id')
    def _compute_crumges_pending_upsell_ids(self):
        for lead in self:
            if not lead.partner_id:
                lead.crumges_pending_upsell_ids = False
                continue
            
            partners = lead.partner_id
            if lead.partner_id.parent_id:
                partners |= lead.partner_id.parent_id
            if lead.partner_id.child_ids:
                partners |= lead.partner_id.child_ids
            
            # Search for pending upsells (draft/sent state, subscription_state=7_upsell)
            upsells = self.env['sale.order'].search([
                ('partner_id', 'in', partners.ids),
                ('state', 'in', ['draft', 'sent']),
                ('subscription_state', '=', '7_upsell')
            ])
            lead.crumges_pending_upsell_ids = upsells
