# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ashok PK (odoo@cybrosys.com)
#
#    Adaptación y mejoras: Crumges
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    """Class to inherit the functions in the website sale"""

    def shop(self, page=0, category=None, search='', min_price=0.0,
             max_price=0.0, ppg=False, **post):
        """Function to inherit shop and to set the posted value in the
        website session."""
        res = super().shop(page=page, category=category, search=search, min_price=min_price,
                           max_price=max_price, ppg=ppg, **post)
        
        # Si el usuario es agente y tiene un cliente seleccionado en sesión
        if request.env.user.partner_id.is_agent:
            agent_customer_id = request.session.get('agent_customer_id')
            if agent_customer_id:
                # Usar el cliente de la sesión, no el del post
                post['customer'] = str(agent_customer_id)
            elif 'customer' not in post:
                # Si no hay cliente en sesión y tampoco en post, usar el agente
                post['customer'] = str(request.env.user.partner_id.id)
        
        # Gestionar cambios de cliente
        if 'post_values' in request.session:
            stored_post_values = request.session['post_values']
            if stored_post_values != post and post:
                order = request.website.sale_get_order()
                if order:
                    order.sudo().unlink()
        
        # Ensure order has correct customer properties before rendering shop
        if request.env.user.partner_id.is_agent:
            agent_customer_id = request.session.get('agent_customer_id')
            if agent_customer_id:
                order = request.website.sale_get_order()
                if order:
                    customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
                    order.sudo().set_agent_customer(customer, request.env.user.partner_id)

        res = super().shop(page=page, category=category, search=search, min_price=min_price,
                           max_price=max_price, ppg=ppg, **post)

        if post:
            request.session['post_values'] = post
        
        return res

    def cart(self, access_token=None, revive='', **post):
        """Function to update the address from cart when the sale order is
        created"""
        # Update order BEFORE calling super to ensure prices are correct for rendering
        if request.env.user.partner_id.is_agent:
            agent_customer_id = request.session.get('agent_customer_id')
            order = request.website.sale_get_order()
            
            if order:
                customer = None
                if agent_customer_id:
                    customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
                elif 'post_values' in request.session:
                    post_values = request.session['post_values']
                    customer_id = post_values.get('customer')
                    if customer_id:
                        customer = request.env['res.partner'].sudo().browse(int(customer_id))
                
                if customer:
                     order.sudo().set_agent_customer(customer, request.env.user.partner_id)

        res = super().cart(access_token=access_token, revive=revive, **post)
        return res

    def _get_shop_payment_values(self, order, **kwargs):
        """Function to update the sale order details created from website"""
        # Update order BEFORE calling super
        if order and request.env.user.partner_id.is_agent:
            agent_customer_id = request.session.get('agent_customer_id')
            customer = None
            
            if agent_customer_id:
                customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
            elif 'post_values' in request.session:
                post_values = request.session['post_values']
                customer_id = post_values.get('customer')
                if customer_id:
                    customer = request.env['res.partner'].sudo().browse(int(customer_id))
            
            if customer:
                order.sudo().set_agent_customer(customer, request.env.user.partner_id)

        res = super()._get_shop_payment_values(order, **kwargs)
        
        # Ensure the response dict also reflects these changes (though order obj is updated)
        if order and request.env.user.partner_id.is_agent:
             # Just in case super re-read something or we want to be safe
             if order.partner_id:
                website_sale_order = res.get('website_sale_order', {})
                website_sale_order.update({
                    'partner_id': order.partner_id.id,
                    'partner_invoice_id': order.partner_invoice_id.id,
                    'partner_shipping_id': order.partner_shipping_id.id,
                    'agent_id': order.agent_id.id,
                    'pricelist_id': order.pricelist_id.id,
                    'fiscal_position_id': order.fiscal_position_id.id,
                })
                res.update({
                    'partner': order.partner_id,
                    'partner_id': order.partner_id.id,
                    'website_sale_order': website_sale_order,
                })

        return res

    def _prepare_shop_payment_confirmation_values(self, order):
        """Function to prepare payment confirmation values"""
        # Ensure consistency one last time, BUT verify state inside set_agent_customer to avoid bad request
        if order and request.env.user.partner_id.is_agent:
            agent_customer_id = request.session.get('agent_customer_id')
            customer = None
            if agent_customer_id:
                customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
            elif 'post_values' in request.session:
                post_values = request.session['post_values']
                customer_id = post_values.get('customer')
                if customer_id:
                     customer = request.env['res.partner'].sudo().browse(int(customer_id))
            
            if customer:
                order.sudo().set_agent_customer(customer, request.env.user.partner_id)

        res = super()._prepare_shop_payment_confirmation_values(order)
        return res

    def checkout_values(self, order, **kw):
        """Updating the billing and shipping address based on customer"""
        res = super().checkout_values(order, **kw)
        
        agent_customer_id = request.session.get('agent_customer_id')
        
        if request.env.user.partner_id.is_agent:
            if agent_customer_id:
                # Si hay cliente en sesión, usar ese
                customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
                res.update({
                    'shippings': customer,
                    'billings': customer,
                })
            elif 'post_values' in request.session:
                # Fallback a post_values si existe
                post_values = request.session['post_values']
                customer_id = post_values.get('customer')
                if customer_id:
                    customer = request.env['res.partner'].sudo().browse(int(customer_id))
                    res.update({
                        'shippings': customer,
                        'billings': customer,
                    })
        
        return res

    def shop_payment_confirmation(self, **post):
        """Function to remove the values of post_values from the session."""
        res = super().shop_payment_confirmation(**post)
        request.session['post_values'] = {}
        request.session['agent_customer_id'] = None
        request.session['agent_id'] = None
        return res


class PaymentPortal(payment_portal.PaymentPortal):
    """Class to inherit the function to change the details of the
    transactions."""
    
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """Function to change the order details for delivery and invoice"""
        if order_id:
            order = request.env['sale.order'].sudo().browse(int(order_id))
            if request.env.user.partner_id.is_agent:
                agent_customer_id = request.session.get('agent_customer_id')
                customer = None
                if agent_customer_id:
                    customer = request.env['res.partner'].sudo().browse(int(agent_customer_id))
                elif 'post_values' in request.session:
                    post_values = request.session['post_values']
                    customer_id = post_values.get('customer')
                    if customer_id:
                         customer = request.env['res.partner'].sudo().browse(int(customer_id))
                
                if customer:
                     order.sudo().set_agent_customer(customer, request.env.user.partner_id)

        res = super().shop_payment_transaction(order_id, access_token, **kwargs)
        return res