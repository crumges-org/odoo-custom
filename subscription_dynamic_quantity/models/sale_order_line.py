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
    )
    
    has_negative_warning = fields.Boolean(
        string='Has Negative Warning',
        compute='_compute_has_negative_warning',
        store=False,
    )

    @api.depends('product_id', 'product_id.recurring_invoice')
    def _compute_is_subscription_line(self):
        """Identify if this line is a subscription product."""
        for line in self:
            line.is_subscription_line = line.product_id.recurring_invoice if line.product_id else False

    def _compute_has_negative_warning(self):
        """Check if this subscription line has negative quantity."""
        for line in self:
            line.has_negative_warning = (
                line.is_subscription_line and line.product_uom_qty < 0
            )

    # ⭐ SOLUCIÓN SIMPLE: Interceptar write en qty_delivered
    def write(self, vals):
        """Update subscription quantities when service deliveries change."""
        res = super().write(vals)
        
        # Solo si cambió qty_delivered
        if 'qty_delivered' in vals:
            # Buscar líneas de servicio que tienen subscription_product_id
            service_lines = self.filtered(
                lambda l: l.product_id.subscription_product_id and l.order_id
            )
            
            # Para cada servicio, actualizar su suscripción relacionada
            for service_line in service_lines:
                subscription_product = service_line.product_id.subscription_product_id
                
                # Buscar la línea de suscripción
                subscription_line = service_line.order_id.order_line.filtered(
                    lambda l: l.product_id == subscription_product and l.id != service_line.id
                )
                
                if subscription_line:
                    # Calcular nueva cantidad
                    new_qty = subscription_line._calculate_subscription_qty()
                    
                    # Actualizar si cambió
                    if subscription_line.product_uom_qty != new_qty:
                        # Usar SQL directo para evitar recursión
                        self.env.cr.execute(
                            "UPDATE sale_order_line SET product_uom_qty = %s WHERE id = %s",
                            (new_qty, subscription_line.id)
                        )
                        subscription_line.invalidate_recordset(['product_uom_qty'])
                        
                        # Log
                        _logger.info(
                            'Auto-updated subscription %s from %s to %s',
                            subscription_line.product_id.name,
                            subscription_line.product_uom_qty,
                            new_qty
                        )
        
        # Si cambió el producto, asegurar líneas de suscripción
        if 'product_id' in vals:
            orders = self.mapped('order_id')
            for order in orders:
                order._ensure_subscription_lines()
        
        return res

    def _calculate_subscription_qty(self):
        """Calculate subscription quantity based on service lines."""
        self.ensure_one()
        
        if not self.is_subscription_line or not self.order_id:
            return 0.0
        
        # Obtener todas las líneas de servicio relacionadas
        service_lines = self.order_id.order_line.filtered(
            lambda l: l.product_id.subscription_product_id == self.product_id
        )
        
        if not service_lines:
            return 0.0
        
        # Sumar instalaciones y desinstalaciones
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
                'Negative subscription qty for %s: %s',
                self.product_id.name, calculated_qty
            )
        
        return calculated_qty

    def action_recalculate_subscription_qty(self):
        """Recalculate and update subscription quantity (manual action)."""
        for line in self:
            if not line.is_subscription_line:
                continue
            
            new_qty = line._calculate_subscription_qty()
            
            if line.product_uom_qty != new_qty:
                line.product_uom_qty = new_qty
                
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Quantity Updated'),
                'message': _('Subscription quantity recalculated: %s') % new_qty,
                'type': 'success',
            }
        }

    @api.onchange('product_id')
    def _onchange_product_id_add_subscription(self):
        """Add subscription product when service is added."""
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
                    'A subscription line for "%s" will be automatically added.'
                ) % subscription_product.name
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure subscription lines are created after services."""
        lines = super().create(vals_list)
        
        orders = lines.mapped('order_id')
        for order in orders:
            order._ensure_subscription_lines()
        
        return lines