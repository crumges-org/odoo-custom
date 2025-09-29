# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    price_percentage = fields.Float(string="Incremento (%)", help="Porcentaje de incremento sobre el precio del producto.")

    @api.depends('price_percentage', 'product_tmpl_id.list_price')
    def _compute_price_extra(self):
        """Calcula el precio adicional basado en el porcentaje."""
        for record in self:
            if record.product_tmpl_id.list_price:
                record.price_extra = (record.product_tmpl_id.list_price * record.price_percentage) / 100

    price_extra = fields.Float(compute="_compute_price_extra", store=True)

    def _inverse_price_extra(self):
        """Permite modificar manualmente el precio extra sin cambiar el porcentaje."""
        pass  # No se actualiza el porcentaje cuando se modifica el precio extra

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_update_button = fields.Boolean(string="Mostrar Botón de Actualización", compute="_compute_show_update_button", store=True)

    @api.depends('list_price', 'product_variant_ids')
    def _compute_show_update_button(self):
        """Muestra el botón solo si el producto tiene variantes y su precio cambia."""
        for product in self:
            product.show_update_button = bool(product.product_variant_count > 1)

    def update_variant_prices(self):
        """Método para actualizar los precios de variantes basado en el porcentaje."""
        for product in self:
            attribute_values = self.env['product.template.attribute.value'].search([
                ('product_tmpl_id', '=', product.id)
            ])
            for attribute_value in attribute_values:
                if attribute_value.product_tmpl_id.list_price:
                    attribute_value.price_extra = (attribute_value.product_tmpl_id.list_price * attribute_value.price_percentage) / 100





