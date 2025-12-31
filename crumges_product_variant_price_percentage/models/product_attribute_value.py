# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    variant_price_percentage = fields.Float(
        string="Price Percentage",
        digits=(16, 3),
        help="Percentage of the product list price to add as extra price."
    )

    @api.onchange('variant_price_percentage')
    def _onchange_variant_price_percentage(self):
        """Update price_extra when percentage changes."""
        for record in self:
            if record.product_tmpl_id:
                record.price_extra = (record.product_tmpl_id.list_price * record.variant_price_percentage) / 100

    @api.onchange('price_extra')
    def _onchange_price_extra(self):
        """Update percentage when price_extra changes manually."""
        for record in self:
            if record.product_tmpl_id and record.product_tmpl_id.list_price:
                record.variant_price_percentage = (record.price_extra / record.product_tmpl_id.list_price) * 100
            elif not record.product_tmpl_id.list_price and record.price_extra:
                 record.variant_price_percentage = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # If percentage is provided but no price_extra, calculate price_extra
            if 'variant_price_percentage' in vals and 'price_extra' not in vals:
                product_tmpl = self.env['product.template'].browse(vals.get('product_tmpl_id'))
                if product_tmpl:
                    vals['price_extra'] = (product_tmpl.list_price * vals['variant_price_percentage']) / 100
            
            # If price_extra is provided but no percentage, calculate percentage
            elif 'price_extra' in vals and 'variant_price_percentage' not in vals:
                 product_tmpl = self.env['product.template'].browse(vals.get('product_tmpl_id'))
                 if product_tmpl and product_tmpl.list_price:
                     vals['variant_price_percentage'] = (vals['price_extra'] / product_tmpl.list_price) * 100

        return super().create(vals_list)

    def write(self, vals):
        # We need to handle updates carefully to allow implicit bi-directional sync
        
        # Case 1: Updating percentage -> Update price_extra
        if 'variant_price_percentage' in vals and 'price_extra' not in vals:
            for record in self:
                # We can't update vals generically for all records if they depend on record-specific data (product price)
                # So we must write to each record if we want to support batch updates with different products.
                # However, usually write is called on a recordset. 
                # If we are in a loop or single record, we can modify vals.
                # If logic is complex, it's better to do super first, then update the others to avoid conflicts?
                # "Anything that edit, must affect the other thing"
                
                # To be safe for batch operations with different products:
                # We will perform the write, then check for discrepancies.
                pass

        # Case 2: Updating price_extra -> Update percentage
        if 'price_extra' in vals and 'variant_price_percentage' not in vals:
             pass

        res = super().write(vals)

        # Post-write sync
        if 'variant_price_percentage' in vals and 'price_extra' not in vals:
            for record in self:
                if record.product_tmpl_id:
                    new_price = (record.product_tmpl_id.list_price * record.variant_price_percentage) / 100
                    if abs(record.price_extra - new_price) > 0.001:
                        record.write({'price_extra': new_price})
        
        elif 'price_extra' in vals and 'variant_price_percentage' not in vals:
            for record in self:
                if record.product_tmpl_id and record.product_tmpl_id.list_price:
                    new_percentage = (record.price_extra / record.product_tmpl_id.list_price) * 100
                    if abs(record.variant_price_percentage - new_percentage) > 0.001:
                        record.write({'variant_price_percentage': new_percentage})

        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        res = super().write(vals)
        if 'list_price' in vals:
            # Update price_extra for all attribute values based on their percentage
            for template in self:
                 # Find values with non-zero percentage
                 attr_values = self.env['product.template.attribute.value'].search([
                     ('product_tmpl_id', '=', template.id),
                     ('variant_price_percentage', '!=', 0.0)
                 ])
                 for val in attr_values:
                     new_price_extra = (template.list_price * val.variant_price_percentage) / 100
                     if abs(val.price_extra - new_price_extra) > 0.001:
                         val.write({'price_extra': new_price_extra})
        return res
