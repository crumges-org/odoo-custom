from odoo import http
from odoo.addons.helpdesk.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        values = super(CustomerPortal, self)._ticket_get_page_view_values(
            ticket, access_token, **kwargs)

        if ticket.parent_id:
            values['parent_id'] = ticket.parent_id
        if ticket.child_ids:
            values['childs'] = ticket.child_ids
        return values
