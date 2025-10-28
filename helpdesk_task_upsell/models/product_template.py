# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Campo para identificar si es una categoría de upsell
    is_upsell_category = fields.Boolean(
        string='Es Categoría de Venta Adicional', 
        default=False,
        help='Marcar si este producto se usa como categoría para ventas adicionales en suscripciones'
    )
    
    # Modo de operación de la categoría
    upsell_mode = fields.Selection([
        ('additional_sale', 'Venta Adicional Directa'),
        ('prepaid_consumption', 'Consumo de Servicio Pre-contratado')
    ], string='Modo de Venta Adicional', default='additional_sale',
       help='Venta Adicional Directa: Crea nueva tarea y línea de venta.\n'
            'Consumo de Servicio Pre-contratado: Crea subtarea en tarea existente y línea informativa.')
    
    # Configuración para modo prepaid_consumption
    parent_service_product_id = fields.Many2one(
        'product.product', 
        string='Producto de Servicio Padre',
        help='Producto que genera la tarea padre donde se crearán las subtareas',
        domain=[('type', '=', 'service')]
    )
    
    dummy_product_id = fields.Many2one(
        'product.product',
        string='Producto Informativo',
        help='Producto que se usará para crear la línea informativa en la suscripción (sin consumir horas)',
        domain=[('type', '=', 'service')]
    )
    
    @api.onchange('upsell_mode')
    def _onchange_upsell_mode(self):
        """Limpiar campos cuando cambia el modo"""
        if self.upsell_mode == 'additional_sale':
            self.parent_service_product_id = False
            self.dummy_product_id = False
    
    @api.constrains('is_upsell_category', 'upsell_mode', 'parent_service_product_id', 'dummy_product_id')
    def _check_upsell_configuration(self):
        """Validar configuración de categorías de upsell"""
        for product in self:
            if product.is_upsell_category and product.upsell_mode == 'prepaid_consumption':
                if not product.parent_service_product_id:
                    raise ValidationError(_('Debe seleccionar un Producto de Servicio Padre para el modo "Consumo de Servicio Pre-contratado".'))
                if not product.dummy_product_id:
                    raise ValidationError(_('Debe seleccionar un Producto Informativo para el modo "Consumo de Servicio Pre-contratado".'))