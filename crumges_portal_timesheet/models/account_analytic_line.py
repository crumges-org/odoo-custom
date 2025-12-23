# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.osv.expression import AND

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _timesheet_get_portal_domain(self):
        """ Override to ensure Portal Users only see their own timesheets or their employee's. """
        domain = super(AccountAnalyticLine, self)._timesheet_get_portal_domain()
        
        # If user is a portal user, strictly filter by their user_id
        if self.env.user.has_group('base.group_portal'):
            domain = AND([domain, [('user_id', '=', self.env.user.id)]])
            
        return domain
