# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.mail.tools.discuss import Store

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _portal_get_default_format_properties_names(self, options=None):
        names = super()._portal_get_default_format_properties_names(options=options)
        names.add('tracking_value_ids')
        return names

    def _portal_message_format(self, properties_names, options=None):
        vals_list = super()._portal_message_format(properties_names, options=options)
        
        from markupsafe import Markup
        
        for message, values in zip(self, vals_list):
            if message.tracking_value_ids:
                # Use standard Odoo mail formatting for tracking values
                # Key must be 'trackingValues' for the frontend component
                tracking_values = message.sudo().tracking_value_ids._tracking_value_format()
                values['trackingValues'] = tracking_values
                
                # FALLBACK: Inject into body to ensure visibility if frontend ignores trackingValues
                tracking_html = '<ul class="o_mail_thread_message_tracking mb-0 list-unstyled" style="color: #555; font-size: 0.9em; margin-top: 8px;">'
                for track in tracking_values:
                    # Get values, handling potential None/False
                    old_val = track.get('oldValue', {}).get('value', '')
                    new_val = track.get('newValue', {}).get('value', '')
                    field_name = track.get('changedField', 'Unknown')
                    
                    arrow = ' &rarr; '
                    content = f'{field_name}: {old_val}{arrow}{new_val}'
                    tracking_html += f'<li>{content}</li>'
                tracking_html += '</ul>'
                
                existing_body = values.get('body') or ''
                values['body'] = Markup(existing_body) + Markup(tracking_html)
                
        return vals_list
