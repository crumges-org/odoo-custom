from odoo import models, api, SUPERUSER_ID
from odoo.http import request
import logging
import logging

_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    def _get_current_pricelist(self):
        """
        Override to prioritize the pricelist of the current sale order (if any)
        assigned to the agent's selected customer, instead of the logged-in user's pricelist.
        """
        if request and request.session.get('sale_order_id'):
            order_id = request.session.get('sale_order_id')
            _logger.info("WEBSITE DEBUG: Checking pricelist for session order %s", order_id)
            order = self.env['sale.order'].sudo().browse(order_id)
            if order and order.pricelist_id:
                _logger.info("WEBSITE DEBUG: Returning Forced Pricelist: %s", order.pricelist_id.name)
                return order.pricelist_id
        
        pl = super(Website, self)._get_current_pricelist()
        _logger.info("WEBSITE DEBUG: Returning Super Pricelist: %s", pl.name if pl else 'None')
        return pl

    def _get_current_fiscal_position(self):
        """
        Override to prioritize the fiscal position of the current sale order (if any)
        assigned to the agent's selected customer.
        """
        if request and request.session.get('sale_order_id'):
            order = self.env['sale.order'].sudo().browse(request.session.get('sale_order_id'))
            if order and order.fiscal_position_id:
                return order.fiscal_position_id

        return super(Website, self)._get_current_fiscal_position()



    def sale_get_order(self, force_create=False):
        """ Return the current sales order after mofications specified by params.
        OVERRIDE: Added logic to prevent resetting partner_id if we are in Agent Shop mode.
        """
        self.ensure_one()
        self = self.with_company(self.company_id)
        SaleOrder = self.env['sale.order'].sudo()

        sale_order_id = request.session.get('sale_order_id')
        
        # AGENT_SHOP: Check if we are in Agent mode
        agent_customer_id = request.session.get('agent_customer_id')

        if sale_order_id:
            sale_order_sudo = SaleOrder.browse(sale_order_id).exists()
        elif self.env.user and not self.env.user._is_public():
            sale_order_sudo = self.env.user.partner_id.last_website_so_id
            if sale_order_sudo:
                # AGENT_SHOP: If in agent mode, we might want to check if the last order belongs to the customer
                if agent_customer_id and sale_order_sudo.partner_id.id != agent_customer_id:
                     # Discard last order of agent if it's not for the selected customer
                     sale_order_sudo = SaleOrder
                else: 
                    available_pricelists = self.get_pricelist_available()
                    so_pricelist_sudo = sale_order_sudo.pricelist_id
                    if so_pricelist_sudo and so_pricelist_sudo not in available_pricelists:
                        # AGENT_SHOP: If in agent mode, we force pricelist availability, so this check might pass now
                        # but if logic is strict, we might need to rely on get_pricelist_available override
                        sale_order_sudo = SaleOrder
                    else:
                        # Do not reload the cart of this user last visit
                        # if the Fiscal Position has changed.
                        fpos = sale_order_sudo.env['account.fiscal.position'].with_company(
                            sale_order_sudo.company_id
                        )._get_fiscal_position(
                            sale_order_sudo.partner_id,
                            delivery=sale_order_sudo.partner_shipping_id
                        )
                        if fpos.id != sale_order_sudo.fiscal_position_id.id:
                            sale_order_sudo = SaleOrder
        else:
            sale_order_sudo = SaleOrder

        # Ignore the current order if a payment has been initiated. We don't want to retrieve the
        # cart and allow the user to update it when the payment is about to confirm it.
        if sale_order_sudo and sale_order_sudo.get_portal_last_transaction().state in (
            'pending', 'authorized', 'done'
        ):
            sale_order_sudo = None

        if not (sale_order_sudo or force_create):
            if request.session.get('sale_order_id'):
                request.session.pop('sale_order_id')
                request.session.pop('website_sale_cart_quantity', None)
            return self.env['sale.order']

        partner_sudo = self.env.user.partner_id

        # AGENT_SHOP: If agent is shopping, the partner on the order SHOULD be the customer
        if agent_customer_id:
             target_partner_id = agent_customer_id
        else:
             target_partner_id = partner_sudo.id

        # cart creation was requested
        if not sale_order_sudo:
            # AGENT_SHOP: Use customer if available
            so_partner = self.env['res.partner'].sudo().browse(target_partner_id)
            so_data = self._prepare_sale_order_values(so_partner)
            sale_order_sudo = SaleOrder.with_user(SUPERUSER_ID).create(so_data)

            request.session['sale_order_id'] = sale_order_sudo.id
            request.session['website_sale_cart_quantity'] = sale_order_sudo.cart_quantity
            return sale_order_sudo.with_user(self.env.user).sudo()

        # Existing Cart
        if not request.session.get('sale_order_id'):
            request.session['sale_order_id'] = sale_order_sudo.id
            request.session['website_sale_cart_quantity'] = sale_order_sudo.cart_quantity

        # check for change of partner_id ie after signup
        # AGENT_SHOP: This is the critical fix.
        # If we are in agent mode, we EXPECT the partner to be different from the logged in user (Agent)
        # So we verify against the expected target_partner_id
        if target_partner_id != sale_order_sudo.partner_id.id:
             sale_order_sudo._update_address(target_partner_id, ['partner_id'])

        return sale_order_sudo
