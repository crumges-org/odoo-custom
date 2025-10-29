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

    # ⭐ SOLUCIÓN: Actualizar suscripciones cuando cambia qty_delivered de servicios
    def write(self, vals):
        """Intercept writes to update subscription quantities when service deliveries change."""
        
        # ⭐ Prevenir loop infinito: si estamos en contexto de actualización automática, salir
        if self.env.context.get('skip_subscription_update'):
            return super().write(vals)
        
        res = super().write(vals)
        
        # Si cambió qty_delivered en líneas de servicio, actualizar suscripciones relacionadas
        if 'qty_delivered' in vals:
            for line in self:
                if line.product_id.subscription_product_id and line.order_id:
                    subscription_product = line.product_id.subscription_product_id
                    
                    # Buscar línea de suscripción
                    subscription_line = line.order_id.order_line.filtered(
                        lambda l: l.product_id == subscription_product
                    )
                    
                    if subscription_line:
                        subscription_line._update_subscription_quantity()
        
        # Si cambió el producto, asegurar líneas de suscripción
        if 'product_id' in vals:
            orders = self.mapped('order_id')
            for order in orders:
                order._ensure_subscription_lines()
        
        return res

    def _update_subscription_quantity(self):
        """
        Calculate and update product_uom_qty for subscription lines based on service deliveries.
        Uses context to prevent infinite loops.
        """
        for line in self:
            if not line.is_subscription_line or not line.order_id:
                continue
            
            service_lines = line.order_id.order_line.filtered(
                lambda l: l.product_id.subscription_product_id == line.product_id
            )
            
            if not service_lines:
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
            
            # Log si es negativo
            if calculated_qty < 0:
                _logger.warning(
                    'Subscription quantity is NEGATIVE for order %s, product %s. '
                    'Installations: %s, Uninstallations: %s, Result: %s',
                    line.order_id.name, line.product_id.name, 
                    installations, uninstallations, calculated_qty
                )
                
                # Mensaje simple en chatter
                if line.order_id and line.order_id.id:
                    try:
                        message = _(
                            "⚠️ <b>Negative Subscription:</b> %s (%s)<br/>"
                            "Installations: %s | Uninstallations: %s<br/>"
                            "Review task hours."
                        ) % (
                            line.product_id.name,
                            calculated_qty,
                            installations,
                            uninstallations
                        )
                        
                        line.order_id.message_post(
                            body=message,
                            message_type='comment',
                            subtype_xmlid='mail.mt_note',
                        )
                    except Exception as e:
                        _logger.debug('Could not post message: %s', e)
            
            # ⭐ Actualizar usando contexto para prevenir loop infinito
            if line.product_uom_qty != calculated_qty:
                _logger.info(
                    'Updating subscription quantity for %s: %s -> %s',
                    line.product_id.name, line.product_uom_qty, calculated_qty
                )
                line.with_context(skip_subscription_update=True).write({
                    'product_uom_qty': calculated_qty
                })

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
            '<td style="padding: 10px; border: 1px solid #dee2e6;"><strong>🔒 Final Quantity</strong></td>'
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
            self.product_uom_qty
        )
        
        if self.has_negative_warning:
            message += _(
                '<div style="background-color: #fff3cd; border-left: 4px solid #ffc107; '
                'padding: 15px; margin-top: 15px;">'
                '<h4 style="margin-top: 0; color: #856404;">⚠️ Negative Quantity</h4>'
                '<p style="margin-bottom: 0;">Review task hours - uninstallations exceed installations.</p>'
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