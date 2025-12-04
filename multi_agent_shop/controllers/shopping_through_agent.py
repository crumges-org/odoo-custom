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
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden


class Agent(http.Controller):
    """Controller for agent shop functionality"""
    
    @http.route(['/agent/shop'], type='http', auth='user', website=True)
    def agent_shop(self, **kw):
        """Display agent shop page with customer selection"""
        # Get the current user
        user = request.env.user
        
        # Check if user is an agent
        is_agent = user.partner_id.is_agent
        
        if not is_agent:
            raise Forbidden("No tienes permiso para acceder a esta página.")
        
        # Get customers assigned to this agent using sudo()
        customer_ids = request.env['res.partner'].sudo().search([
            ('agent_id', '=', user.partner_id.id)
        ])
        
        return request.render('multi_agent_shop.agent_shop_template', {
            'customer_ids': customer_ids
        })
    
    @http.route(['/agent/shop/customer'], type='http', auth='user', website=True, methods=['POST'])
    def agent_shop_customer(self, **post):
        """Handle customer selection and redirect to shop"""
        # Get current user
        user = request.env.user
        
        # Check if user is an agent
        is_agent = user.partner_id.is_agent
        
        if not is_agent:
            raise Forbidden("No tienes permiso para realizar esta acción.")
        
        customer_id = int(post.get('customer', 0))
        
        if not customer_id:
            return request.redirect('/agent/shop')
        
        # Verify that the customer is assigned to the agent using sudo()
        customer = request.env['res.partner'].sudo().browse(customer_id)
        user_partner = user.partner_id
        
        # Check if customer is assigned to this agent
        if customer.agent_id.id != user_partner.id:
            raise Forbidden("Este cliente no está asignado a tu cuenta.")
        
        # Get or create sale order for the customer (NOT the agent)
        # The key is to use the CUSTOMER as the partner, not the agent
        sale_order = request.website.sale_get_order(force_create=True)
        
        # Update the order to use the customer instead of the agent
        if sale_order and sale_order.partner_id.id != customer_id:
            sale_order.write({
                'partner_id': customer_id,
                'agent_id': user_partner.id,  # Store the agent reference
            })
        
        # Store customer in session with explicit key
        request.session['agent_customer_id'] = customer_id
        request.session['agent_customer_name'] = customer.name
        request.session['agent_id'] = user_partner.id
        request.session.modified = True
        
        # Redirect to shop
        return request.redirect('/shop')