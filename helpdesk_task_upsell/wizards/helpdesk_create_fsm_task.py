# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskCreateFsmTask(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'
    _description = 'Helpdesk Create FSM Task Wizard'

    # Campos para venta adicional
    is_upsell = fields.Boolean(string='Es Venta Adicional', default=False)
    subscription_id = fields.Many2one('sale.order', string='Suscripción')
    upsell_product_id = fields.Many2one(
        'product.product',
        string='Categoría de Servicio',
        domain=[('is_upsell_category', '=', True)]
    )
    additional_description = fields.Text(string='Información Adicional')
    quantity = fields.Float("Cantidad", default=1.0)
    
    # Campos computados para mostrar información
    upsell_mode = fields.Selection(
        related='upsell_product_id.upsell_mode',
        readonly=True
    )
    parent_task_id = fields.Many2one(
        'project.task',
        string='Tarea Padre',
        compute='_compute_parent_task',
        help='Tarea existente donde se creará la subtarea'
    )
    
    @api.depends('upsell_product_id', 'subscription_id')
    def _compute_parent_task(self):
        """Buscar tarea padre si el modo es prepaid_consumption"""
        for wizard in self:
            wizard.parent_task_id = False
            if (wizard.upsell_product_id and 
                wizard.upsell_product_id.upsell_mode == 'prepaid_consumption' and
                wizard.upsell_product_id.parent_service_product_id and
                wizard.subscription_id):
                
                # Buscar tarea del producto padre en la suscripción
                wizard.parent_task_id = wizard._find_parent_task()
    
    def _find_parent_task(self):
        """Buscar tarea existente del producto padre"""
        parent_product = self.upsell_product_id.parent_service_product_id
        
        # Buscar en líneas de la suscripción
        task = self.env['project.task'].search([
            ('sale_line_id.order_id', '=', self.subscription_id.id),
            ('sale_line_id.product_id', '=', parent_product.id),
            ('active', '=', True)
        ], limit=1)
        
        return task

    def action_generate_task(self):
        """Generar tarea o subtarea según configuración"""
        self.ensure_one()
        
        if not self.is_upsell:
            # Comportamiento estándar
            return super(HelpdeskCreateFsmTask, self).action_generate_task()
        
        if not self.upsell_product_id:
            raise UserError(_('Debe seleccionar una categoría de servicio.'))
        
        # Crear nombre descriptivo
        task_name = f"{self.upsell_product_id.name}: {self.additional_description}"
        
        # Determinar si crear tarea nueva o subtarea
        if self.upsell_product_id.upsell_mode == 'prepaid_consumption' and self.parent_task_id:
            task = self._create_subtask(task_name)
        else:
            task = self._create_new_task(task_name)
        
        # Actualizar el ticket
        self.helpdesk_ticket_id.write({
            'has_upsell': True,
            'upsell_product_id': self.upsell_product_id.id,
            'subscription_id': self.subscription_id.id,
        })
        
        return task
    
    def _create_subtask(self, name):
        """Crear subtarea en tarea padre"""
        # Crear la subtarea
        subtask = self.env['project.task'].create({
            'name': name,
            'parent_id': self.parent_task_id.id,
            'project_id': self.parent_task_id.project_id.id,
            'partner_id': self.partner_id.id,
            'helpdesk_ticket_id': self.helpdesk_ticket_id.id,
            'description': self.additional_description,
            'allocated_hours': self.quantity,
        })
        
        # Crear línea informativa si hay producto dummy configurado
        if self.upsell_product_id.dummy_product_id:
            line = self.env['sale.order.line'].create({
                'product_id': self.upsell_product_id.dummy_product_id.id,
                'name': name,
                'product_uom_qty': 0,  # Sin cantidad
                'price_unit': 0,  # Sin precio
                'order_id': self.subscription_id.id,
                'task_id': subtask.id,
                'is_downpayment': True,  # Marcar como especial
            })
            self.subscription_id.write({'order_line': [(4, line.id)]})
        
        return subtask
    
    def _create_new_task(self, name):
        """Crear tarea nueva con línea de venta"""
        # Crear la tarea usando el método padre
        task = super(HelpdeskCreateFsmTask, self).action_generate_task()
        
        # Actualizar con información adicional
        task.write({
            'name': name,
            'description': self.additional_description,
            'allocated_hours': self.quantity,
        })
        
        # Crear línea de venta
        product = self.upsell_product_id
        if product.type == 'service':
            line = self.env['sale.order.line'].create({
                'product_id': product.id,
                'name': name,
                'product_uom_qty': self.quantity,
                'order_id': self.subscription_id.id,
                'task_id': task.id,
                'project_id': task.project_id.id,
            })
            self.subscription_id.write({'order_line': [(4, line.id)]})
            task.write({'sale_line_id': line.id})
        
        return task