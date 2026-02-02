from odoo import models, _
from markupsafe import Markup

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_upsell_from_lead(self):
        self.ensure_one()
        # Create the upsell order using native mechanism
        
        # Check for pending upsells unless warning is skipped
        if not self.env.context.get('skip_upsell_warning'):
             pending_upsells = self.env['sale.order'].search([
                ('subscription_id', '=', self.id),
                ('state', 'in', ['draft', 'sent']),
                ('subscription_state', '=', '7_upsell')
            ])
             if pending_upsells:
                msg = _(
                    "<p>Esta suscripción ya cuenta con ventas adicionales que no han sido confirmadas.</p>"
                    "<p>Puedes editar estas ventas adicionales desde la solapa 'Ventas adicionales'.</p>"
                    "<p><strong>¿Seguro que quieres agregar otra venta adicional?</strong></p>"
                )
                wizard = self.env['crumges.upsell.warning.wizard'].create({
                    'message': msg,
                    'subscription_id': self.id,
                })
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Upsell Warning'),
                    'res_model': 'crumges.upsell.warning.wizard',
                    'res_id': wizard.id,
                    'view_mode': 'form',
                    'target': 'new',
                }

        action = self.prepare_upsell_order()
        
        # Link to the Opportunity if context provides the ID
        crm_lead_id = self.env.context.get('crm_lead_upsell_id')
        if crm_lead_id and action.get('res_id'):
            upsell_order = self.env['sale.order'].browse(action['res_id'])
            
            # We use sudo() to ensure we can read/write the lead info if needed, 
            # though usually the user has access.
            lead = self.env['crm.lead'].browse(crm_lead_id)
            if lead.exists():
                upsell_order.opportunity_id = lead.id
                
                # Append Lead name to origin
                prefix = lead.name
                if upsell_order.origin:
                    upsell_order.origin = f"{upsell_order.origin}, {prefix}"
                else:
                    upsell_order.origin = prefix
                    
                # Message in Chatter (Both in Subscription and New Order)
                # Message in Chatter (Both in Subscription and New Order)
                msg_body = Markup(_("Upsell created from Opportunity: %s")) % (
                    Markup("<a href='#' data-oe-model='crm.lead' data-oe-id='%d'>%s</a>") % (lead.id, lead.name)
                )
                upsell_order.message_post(body=msg_body)
                if self.is_subscription:
                     self.message_post(body=msg_body)

        return action

    def action_view_upsell_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Upsell Order'),
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
