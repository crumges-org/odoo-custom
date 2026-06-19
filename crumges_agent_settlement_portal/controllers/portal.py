from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class PortalSettlement(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'settlement_count' in counters:
            partner = request.env.user.partner_id
            values['settlement_count'] = request.env['commission.settlement'].sudo().search_count([
                ('agent_id', '=', partner.id)
            ])
        return values

    @http.route(['/my/settlements', '/my/settlements/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_settlements(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Settlement = request.env['commission.settlement'].sudo()

        domain = [('agent_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date_from desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        settlement_count = Settlement.search_count(domain)
        pager = portal_pager(
            url="/my/settlements",
            url_args={'sortby': sortby},
            total=settlement_count,
            page=page,
            step=self._items_per_page
        )
        settlements = Settlement.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'settlements': settlements,
            'page_name': 'settlement',
            'pager': pager,
            'default_url': '/my/settlements',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("crumges_agent_settlement_portal.portal_my_settlements", values)

    @http.route(['/my/settlements/<int:settlement_id>'], type='http', auth="public", website=True)
    def portal_my_settlement_detail(self, settlement_id=None, access_token=None, report_type=None, download=False, **kw):
        try:
            settlement_sudo = self._document_check_access('commission.settlement', settlement_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')

        if report_type == 'pdf':
            return self._show_report(model=settlement_sudo, report_type='pdf', report_ref='commission_oca.action_report_settlement', download=download)

        values = self._settlement_get_page_view_values(settlement_sudo, access_token, **kw)
        return request.render("crumges_agent_settlement_portal.portal_settlement_page", values)

    def _settlement_get_page_view_values(self, settlement, access_token, **kwargs):
        values = {
            'page_name': 'settlement',
            'settlement': settlement,
        }
        return self._get_page_view_values(settlement, access_token, values, 'my_settlements_history', False, **kwargs)
