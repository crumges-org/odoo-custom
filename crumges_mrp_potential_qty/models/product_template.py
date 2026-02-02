from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_potential_qty = fields.Float(
        string='Potential Manufacturing Qty',
        compute='_compute_mrp_potential_qty',
        help='Quantity specifically that can be potentially manufactured with available components (Sum of variants potential).'
    )
    mrp_has_bom = fields.Boolean(
        compute='_compute_mrp_potential_qty',
        string='Has Manufacturing BoM',
        help='Technical field to toggle visibility.'
    )

    @api.depends('product_variant_ids', 'product_variant_ids.mrp_potential_qty', 'product_variant_ids.mrp_has_bom')
    def _compute_mrp_potential_qty(self):
        for template in self:
            template.mrp_potential_qty = sum(template.product_variant_ids.mapped('mrp_potential_qty'))
            template.mrp_has_bom = any(template.product_variant_ids.mapped('mrp_has_bom'))

    def action_view_mrp_bom_structure(self):
        self.ensure_one()
        # For template, we might have multiple variants. 
        # Ideally, we open the structure for the first variant or the template itself if no variants specific BoM.
        # MRP BOM Structure report usually works on Product ID or Template ID.
        
        # Check standard action behavior.
        # We will try to find a BoM for this template.
        # bom = self.env['mrp.bom']._bom_find(self, bom_type='normal')[self]
        # _bom_find expects product.product usually or fails on tmpl_id access on recordset.
        # Let's search manually or via first variant.
        bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.id), ('type', '=', 'normal')], limit=1)
        if not bom and self.product_variant_ids:
             bom = self.env['mrp.bom']._bom_find(self.product_variant_ids[:1], bom_type='normal')[self.product_variant_ids[:1]]
        
        if bom:
            action = self.env["ir.actions.actions"]._for_xml_id("mrp.action_report_mrp_bom")
            action['context'] = {
                'active_id': bom.id,
                'active_model': 'mrp.bom',
                'activate_availabilities': True
            }
            return action
        
        return False
