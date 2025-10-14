# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_subscription_line = fields.Boolean(
        string='Is Subscription Line',
        compute='_compute_is_subscription_line',
        store=True,
        help='Technical field to identify subscription lines managed by this module',
    )
    
    linked_service_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='id',
        compute='_compute_linked_service_lines',
        string='Linked Service Lines',
        help='Service lines (installations/uninstallations) that affect this subscription quantity',
    )
    
    has_negative_warning = fields.Boolean(
        string='Has Negative Warning',
        compute='_compute_has_negative_warning',
        store=False,
        help='Indicates if this line would have negative quantity without protection',
    )

    @api.depends('product_id', 'product_id.recurring_invoice')
    def _compute_is_subscription_line(self):
        """Identify if this line is a subscription product."""
        for line in self:
            line.is_subscription_line = line.product_id.recurring_invoice if line.product_id else False

    def _compute_linked_service_lines(self):
        """Find all service lines in the same order that link to this subscription product."""
        for line in self:
            if line.is_subscription_line and line.order_id:
                linked_lines = line.order_id.order_line.filtered(
                    lambda l: l.product_id.subscription_product_id == line.product_id and l.id != line.id
                )
                line.linked_service_line_ids = linked_lines
            else:
                line.linked_service_line_ids = False

    def _compute_has_negative_warning(self):
        """Check if this subscription line would be negative without protection."""
        for line in self:
            if not line.is_subscription_line or not line.order_id:
                line.has_negative_warning = False
                continue
            
            service_lines = line.order_id.order_line.filtered(
                lambda l: l.product_id.subscription_product_id == line.product_id
            )
            
            installations = sum(
                service_lines.filtered(
                    lambda l: l.product_id.subscription_service_type == 'installation'
                ).mapped('qty_delivered')
            )
            
            uninstallations = sum(
                service_lines.filtered(
                    lambda l: l.product_id.subscription_service_type == 'uninstallation'
                ).mapped('qty_delivered')
            )
            
            line.has_negative_warning = (installations - uninstallations) < 0

    @api.depends('product_id', 'product_id.subscription_product_id', 
                 'order_id.order_line.qty_delivered', 'order_id.order_line.product_id')
    def _compute_qty_delivered(self):
        """
        Override qty_delivered computation for subscription lines.
        Calculate: SUM(delivered installations) - SUM(delivered uninstallations)
        If negative, force to 0 and create message in chatter.
        """
        subscription_lines = self.filtered('is_subscription_line')
        other_lines = self - subscription_lines
        
        if other_lines:
            super(SaleOrderLine, other_lines)._compute_qty_delivered()
        
        for line in subscription_lines:
            if not line.order_id:
                line.qty_delivered = 0.0
                continue
            
            service_lines = line.order_id.order_line.filtered(
                lambda l: l.product_id.subscription_product_id == line.product_id
            )
            
            if not service_lines:
                line.qty_delivered = 0.0
                continue
            
            installations = sum(
                service_lines.filtered(
                    lambda l: l.product_id.subscription_service_type == 'installation'
                ).mapped('qty_delivered')
            )
            
            uninstallations = sum(
                service_lines.filtered(
                    lambda l: l.product_id.subscription_service_type == 'uninstallation'
                ).mapped('qty_delivered')
            )
            
            calculated_qty = installations - uninstallations
            
            if calculated_qty < 0:
                _logger.warning(
                    'Subscription quantity would be negative for order %s, product %s. '
                    'Installations: %s, Uninstallations: %s. Forcing to 0.',
                    line.order_id.name, line.product_id.name, installations, uninstallations
                )
                
                line.order_id.message_post(
                    body=_(
                        '<div style="padding: 15px; border-left: 4px solid #ffc107; background-color: #fff3cd;">'
                        '<h4 style="margin-top: 0; color: #856404;">⚠️ Subscription Quantity Adjusted</h4>'
                        
                        '<table style="width: 100%%; margin: 10px 0;">'
                        '<tr><td><strong>Product:</strong></td><td>%s</td></tr>'
                        '<tr><td><strong>Calculated Quantity:</strong></td>'
                        '<td><span style="color: #dc3545;">%s - %s = %s</span></td></tr>'
                        '<tr><td><strong>Adjusted To:</strong></td>'
                        '<td><span style="color: #28a745; font-weight: bold;">0</span></td></tr>'
                        '</table>'
                        
                        '<div style="margin: 10px 0; padding: 10px; background-color: #fff; border-radius: 4px;">'
                        '<strong>📊 Details:</strong><br/>'
                        '<ul style="margin: 5px 0; padding-left: 20px;">'
                        '<li>Total Installations Delivered: <strong>%s</strong></li>'
                        '<li>Total Uninstallations Delivered: <strong>%s</strong></li>'
                        '<li>Difference: <strong style="color: #dc3545;">%s</strong></li>'
                        '</ul>'
                        '</div>'
                        
                        '<div style="margin-top: 10px;">'
                        '<strong>💡 What happened?</strong><br/>'
                        'The subscription quantity has been automatically adjusted to <strong>0</strong> '
                        'to prevent negative values. This occurs when uninstallations in this order '
                        'exceed installations in the same order.<br/><br/>'
                        '<strong>✅ Action:</strong> The order will proceed normally with 0 subscription quantity.'
                        '</div>'
                        '</div>'
                    ) % (
                        line.product_id.name,
                        installations,
                        uninstallations,
                        calculated_qty,
                        installations,
                        uninstallations,
                        calculated_qty
                    ),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
                
                line.qty_delivered = 0.0
            else:
                line.qty_delivered = calculated_qty

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_add_subscription(self):
        """
        When a service product (with linked subscription) is added to the order,
        automatically add the subscription product line if it doesn't exist.
        """
        if not self.product_id or not self.product_id.subscription_product_id:
            return
        
        if not self.order_id:
            return
        
        subscription_product = self.product_id.subscription_product_id
        
        existing_subscription = self.order_id.order_line.filtered(
            lambda l: l.product_id == subscription_product and l.id != self.id
        )
        
        if existing_subscription:
            return
        
        return {
            'warning': {
                'title': _('Subscription Product Will Be Added'),
                'message': _(
                    'A subscription line for "%s" will be automatically added to this order. '
                    'The quantity will be calculated based on delivered installations/uninstallations.'
                ) % subscription_product.name
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        """After creating service lines, ensure subscription lines are created."""
        lines = super().create(vals_list)
        
        orders = lines.mapped('order_id')
        for order in orders:
            order._ensure_subscription_lines()
        
        return lines

    def write(self, vals):
        """After updating lines, ensure subscription lines exist and recalculate."""
        res = super().write(vals)
        
        if 'product_id' in vals:
            orders = self.mapped('order_id')
            for order in orders:
                order._ensure_subscription_lines()
        
        # Si se modifica qty_delivered en una línea de servicio, recalcular suscripciones
        if 'qty_delivered' in vals:
            for line in self:
                if line.product_id.subscription_product_id:
                    # Buscar la línea de suscripción correspondiente
                    subscription_line = line.order_id.order_line.filtered(
                        lambda l: l.product_id == line.product_id.subscription_product_id
                    )
                    if subscription_line:
                        # Forzar recálculo
                        subscription_line._compute_qty_delivered()
        
        return res

    def action_view_subscription_details(self):
        """Show subscription details popup."""
        self.ensure_one()
        
        if not self.is_subscription_line:
            return
        
        service_lines = self.order_id.order_line.filtered(
            lambda l: l.product_id.subscription_product_id == self.product_id
        )
        
        installations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'installation'
            ).mapped('qty_delivered')
        )
        
        uninstallations = sum(
            service_lines.filtered(
                lambda l: l.product_id.subscription_service_type == 'uninstallation'
            ).mapped('qty_delivered')
        )
        
        calculated = installations - uninstallations
        
        message = _(
            '<div style="font-family: Arial, sans-serif;">'
            '<h3 style="color: #007bff;">📊 Subscription Details: %s</h3>'
            '<table style="width: 100%%; border-collapse: collapse; margin: 15px 0;">'
            '<tr style="background-color: #f8f9fa;">'
            '<th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Metric</th>'
            '<th style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">Value</th>'
            '</tr>'
            '<tr><td style="padding: 10px; border: 1px solid #dee2e6;">✅ Installations Delivered</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr style="background-color: #f8f9fa;">'
            '<td style="padding: 10px; border: 1px solid #dee2e6;">❌ Uninstallations Delivered</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr><td style="padding: 10px; border: 1px solid #dee2e6;">➖ Calculated Quantity</td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;"><strong>%s</strong></td></tr>'
            '<tr style="background-color: %s;">'
            '<td style="padding: 10px; border: 1px solid #dee2e6;"><strong>🔒 Final Quantity (Protected)</strong></td>'
            '<td style="padding: 10px; text-align: right; border: 1px solid #dee2e6;">'
            '<strong style="font-size: 18px; color: %s;">%s</strong></td></tr>'
            '</table>'
            '</div>'
        ) % (
            self.product_id.name,
            installations,
            uninstallations,
            calculated,
            '#fff3cd' if self.has_negative_warning else '#d4edda',
            '#dc3545' if self.has_negative_warning else '#28a745',
            self.qty_delivered
        )
        
        if self.has_negative_warning:
            message += _(
                '<div style="background-color: #fff3cd; border-left: 4px solid #ffc107; '
                'padding: 15px; margin-top: 15px;">'
                '<h4 style="margin-top: 0; color: #856404;">⚠️ Protection Applied</h4>'
                '<p style="margin-bottom: 0;">The quantity was adjusted to <strong>0</strong> to prevent negative values. '
                'This is normal when uninstallations exceed installations in this order. '
                'Check the chatter for detailed information.</p>'
                '</div>'
            )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Subscription Information'),
                'message': message,
                'type': 'warning' if self.has_negative_warning else 'success',
                'sticky': True,
            }
        }

    def action_view_linked_services(self):
        """Show linked service lines."""
        self.ensure_one()
        
        if not self.is_subscription_line:
            return
        
        service_lines = self.order_id.order_line.filtered(
            lambda l: l.product_id.subscription_product_id == self.product_id
        )
        
        return {
            'name': _('Linked Service Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', service_lines.ids)],
            'context': {'create': False, 'edit': False, 'delete': False},
        }