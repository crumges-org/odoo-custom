# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.http import request
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from datetime import datetime

class CrumgesTimesheetPortal(TimesheetCustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        # Strategy adopted from portal_user_timesheet_access:
        # If the user has projects (is a collaborator) but no timesheets yet (count=0),
        # normal Odoo hides the menu. We force it to 1 to show the menu.
        # This is a "Data First" fix instead of hacking the view.
        
        # Ensure project_count is computed
        if 'project_count' not in values:
             Project = request.env['project.project']
             values['project_count'] = Project.search_count([]) if Project.check_access_rights('read', raise_exception=False) else 0

        # Check if we should force visibility
        # The logic: If user sees projects, they should see timesheets option to add hours.
        if values.get('project_count', 0) > 0:
            if values.get('timesheet_count', 0) == 0:
                values['timesheet_count'] = 1
        
        return values

    @http.route(['/create/new/timesheet'], type='http', auth="user", website=True)
    def portal_new_timesheet(self, **kw):
        """ Render the form to create a new timesheet """
        values = self._prepare_portal_layout_values()
        
        # Determine allowed projects for the portal user
        domain_project = [('allow_timesheets', '=', True)]
        if request.env.user.has_group('base.group_portal'):
             domain_project += [('privacy_visibility', '=', 'portal')]
             # Add rule to filter projects relevant to the user (e.g. they are following)
             # Standard Odoo portal rules usually filter by 'message_partner_ids'
             domain_project += [('message_partner_ids', 'child_of', [request.env.user.partner_id.id])]
        
        projects = request.env['project.project'].sudo().search(domain_project)
        
        # Pre-select employee if linked
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.uid)], limit=1)

        values.update({
            'projects': projects,
            'employee': employee,
            'page_name': 'timesheet_creates',
            'current_date': fields.Date.today(),
            'default_url': '/my/timesheets',
        })
        return request.render("crumges_portal_timesheet.portal_create_timesheet_form", values)

    @http.route(['/create/timesheet'], type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def create_timesheet_submit(self, **post):
        """ Handle Form Submission """
        try:
            # 1. Validation & Extraction
            project_id = int(post.get('project_id')) if post.get('project_id') else False
            task_id = int(post.get('task_id')) if post.get('task_id') else False
            date_str = post.get('date')
            description = post.get('name')
            
            try:
                hours = int(post.get('unit_amount_hours', 0))
                minutes = int(post.get('unit_amount_minutes', 0))
            except ValueError:
                raise ValidationError(_("Invalid format for hours/minutes."))

            if not project_id:
                raise ValidationError(_("Project is required."))
            if not description:
                raise ValidationError(_("Description is required."))
            
            # Date Validation
            date_value = fields.Date.today()
            if date_str:
                date_value = fields.Date.to_date(date_str)
                if date_value > fields.Date.today():
                    raise ValidationError(_("You cannot log time for future dates."))

            unit_amount = hours + (minutes / 60.0)
            if unit_amount <= 0:
                raise ValidationError(_("Duration must be greater than 0."))

            # 2. Values Preparation
            vals = {
                'name': description,
                'project_id': project_id,
                'task_id': task_id,
                'date': date_value,
                'unit_amount': unit_amount,
                'user_id': request.env.uid,
                # 'employee_id': ... Odoo automagically computes this from user_id if not provided, usually.
            }
            
            # Check/Create Employee link if needed. 
            # Ideally we let Odoo handle employee mapping via user_id.

            # 3. Create Record
            # Use sudo() but rely on security rules we added or inherent checks. 
            # Ideally, if we gave access rights in CSV, we don't need sudo() for the create itself,
            # but we might need it for related checks or if the user is strict portal.
            # Using sudo() ensures it works, but we override user_id to prevent impersonation.
            timesheet = request.env['account.analytic.line'].sudo().create(vals)
            
            return request.redirect('/my/timesheets')

        except Exception as e:
            # Redirect back with error message
            # We need to preserve input values ideally, but for now just error.
            return request.redirect('/create/new/timesheet?error_msg=%s' % str(e))

    @http.route(['/timesheet/project_tasks'], type='json', auth="user", methods=['POST'], website=True)
    def project_tasks_json(self, project_id, **kw):
        """ Return tasks for the given project (for JS dropdown) """
        if not project_id:
            return []
            
        domain = [('project_id', '=', int(project_id))]
        # Add visibility checks if needed
        tasks = request.env['project.task'].sudo().search_read(
            domain, ['id', 'name']
        )
        return tasks

    @http.route(['/my/timesheet/delete/<int:timesheet_id>'], type='http', auth="user", website=True)
    def delete_timesheet(self, timesheet_id, **kw):
        try:
            ts = request.env['account.analytic.line'].sudo().browse(timesheet_id)
            # Ensure ownership
            if ts.user_id.id != request.env.uid:
                return request.redirect('/my/timesheets?error_msg=You cannot delete this timesheet.')
            
            ts.unlink()
            return request.redirect('/my/timesheets')
        except Exception as e:
             return request.redirect('/my/timesheets?error_msg=%s' % str(e))
