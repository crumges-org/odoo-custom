# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR, AND

class MultiAgentCustomerPortal(CustomerPortal):

    def _prepare_orders_domain(self, partner):
        domain = super(MultiAgentCustomerPortal, self)._prepare_orders_domain(partner)
        if partner.is_agent:
            # Show orders for agents using OR condition:
            # 1. Orders created via portal with agent_id explicitly set (new orders)
            # 2. Orders where the internal salesperson (user_id) matches this agent's partner
            #    This covers historical orders created before the module was installed,
            #    where agent_id was never populated.
            return [
                '|',
                ('agent_id', '=', partner.id),
                ('user_id.partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done', 'cancel']),
            ]
        return domain

    def _get_sale_searchbar_sortings(self):
        values = super(MultiAgentCustomerPortal, self)._get_sale_searchbar_sortings()
        values.update({
            'partner_id': {'label': _('Cliente'), 'order': 'partner_id'},
            'invoice_status': {'label': _('Estado de factura'), 'order': 'invoice_status'},
            'delivery_status': {'label': _('Estado de entrega'), 'order': 'delivery_status'},
            'commitment_date': {'label': _('Fecha programada de entrega'), 'order': 'commitment_date'},
        })
        return values

    def _get_sale_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Buscar en todo')},
            'customer': {'input': 'customer', 'label': _('Buscar por Cliente')},
            'sale_order': {'input': 'sale_order', 'label': _('Buscar por Orden')},
        }

    def _get_sale_searchbar_filters(self):
        return {
            'all': {'label': _('Todos'), 'domain': []},
            'invoiced': {'label': _('Facturado'), 'domain': [('invoice_status', '=', 'invoiced')]},
            'to_invoice': {'label': _('A facturar'), 'domain': [('invoice_status', '=', 'to invoice')]},
            'no': {'label': _('Nada a facturar'), 'domain': [('invoice_status', '=', 'no')]},
            'delivery_full': {'label': _('Entregado Totalmente'), 'domain': [('delivery_status', '=', 'full')]},
            'delivery_partial': {'label': _('Entregado Parcialmente'), 'domain': [('delivery_status', '=', 'partial')]},
            'delivery_pending': {'label': _('Entrega Pendiente'), 'domain': [('delivery_status', '=', 'pending')]},
        }

    def _prepare_sale_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, 
        filterby=None, search=None, search_in='all', **kwargs
    ):
        # We call super to get base values, though it computed orders WITHOUT search/filters.
        # We will recompute pager and orders if search or filter are used or we just recompute always to be safe.
        SaleOrder = request.env['sale.order']
        partner = request.env.user.partner_id
        
        # Get standard domain
        if quotation_page:
            domain = self._prepare_quotations_domain(partner)
            url = "/my/quotes"
        else:
            domain = self._prepare_orders_domain(partner)
            url = "/my/orders"
            
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = self._get_sale_searchbar_sortings()
        searchbar_inputs = self._get_sale_searchbar_inputs()
        searchbar_filters = self._get_sale_searchbar_filters()

        # Check default values
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'
            
        sort_order = searchbar_sortings.get(sortby, searchbar_sortings.get('date'))['order']
        domain += searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # Search
        if search and search_in:
            search_domain = []
            if search_in in ('all', 'sale_order'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('all', 'customer'):
                search_domain = OR([search_domain, [('partner_id.name', 'ilike', search)]])
            domain += search_domain

        # URL arguments for pager
        url_args = {}
        if date_begin and date_end:
            url_args.update({'date_begin': date_begin, 'date_end': date_end})
        if sortby:
            url_args['sortby'] = sortby
        if filterby:
            url_args['filterby'] = filterby
        if search and search_in:
            url_args.update({'search': search, 'search_in': search_in})

        # Pager
        total_count = SaleOrder.search_count(domain) if SaleOrder.has_access('read') else 0
        pager_values = portal_pager(
            url=url,
            total=total_count,
            page=page,
            step=self._items_per_page,
            url_args=url_args,
        )

        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset']) if SaleOrder.has_access('read') else SaleOrder

        values = self._prepare_portal_layout_values()
        values.update({
            'date': date_begin,
            'quotations': orders.sudo() if quotation_page else SaleOrder,
            'orders': orders.sudo() if not quotation_page else SaleOrder,
            'page_name': 'quote' if quotation_page else 'order',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })

        return values
