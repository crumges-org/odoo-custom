# -*- coding: utf-8 -*-

from odoo.addons.mail.tools.discuss import Store
from odoo.addons.portal.controllers.mail import PortalChatter
from odoo import http
from odoo.http import request
from odoo.osv import expression
from werkzeug.exceptions import Forbidden
from odoo.exceptions import AccessError

class CrumgesPortalChatter(PortalChatter):

    @http.route('/mail/chatter_fetch', type='json', auth='public', website=True)
    def portal_message_fetch(self, thread_model, thread_id, limit=10, after=None, before=None, **kw):
        """
        Override to allow full chatter history (internal notes, tracking) 
        for portal users who are also employees.
        """
        user = request.env.user
        # Check if user is Not Internal (Portal) AND has Linked Employees
        # We rely on 'employee_ids' field on res.users (from hr module)
        if not user._is_internal() and user.employee_ids:
            
            # 1. Verify Access Rights
            # We must ensure the user has access to the record itself before showing chatter
            thread = request.env[thread_model].browse(thread_id).exists()
            if not thread:
                 return super().portal_message_fetch(thread_model, thread_id, limit=limit, after=after, before=before, **kw)

            can_access = False
            # a) Try standard access
            try:
                thread.check_access_rights('read')
                thread.check_access_rule('read')
                can_access = True
            except AccessError:
                pass
            
            # b) If no standard access, check Token (same logic as original)
            if not can_access and kw.get('token'):
                access_as_sudo = request.env[thread_model]._get_thread_with_access(
                    thread_id, token=kw.get("token")
                )
                if access_as_sudo:
                    can_access = True
            
            if not can_access:
                raise Forbidden()

            # 2. Build Domain for Full History
            # We intentionally do NOT use 'website_message_ids' which excludes internal notes.
            # We intentionally do NOT filter by subtype='mt_comment' to show system notes/tracking.
            
            domain = [
                ("model", "=", thread_model),
                ("res_id", "=", thread_id),
                ("message_type", "!=", "user_notification"), # Exclude specific user notifications if any
            ]
            
            # Add non-empty check (body or attachments OR tracking values)
            # We construct a custom domain to include tracking messages which might have empty body
            extended_non_empty_domain = ['|', '|', ('body', '!=', ''), ('attachment_ids', '!=', False), ('tracking_value_ids', '!=', False)]
            
            domain = expression.AND([
                self._setup_portal_message_fetch_extra_domain(kw),
                domain,
                extended_non_empty_domain,
            ])
            
            # 3. Fetch Messages as SUDO
            # This bypasses ir.rule on mail.message and MailMessage._search restrictions
            Message = request.env["mail.message"].sudo()
            
            # Use _message_fetch from mail.message
            res = Message._message_fetch(domain, None, before, after, None, limit)
            messages = res.pop("messages")
            
            return {
                **res,
                "data": {"mail.message": messages.portal_message_format(options=kw)},
                "messages": Store.many_ids(messages),
            }

        return super().portal_message_fetch(thread_model, thread_id, limit=limit, after=after, before=before, **kw)
