from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    mrp_potential_qty = fields.Float(
        string='Potential Manufacturing Qty',
        compute='_compute_mrp_potential_qty',
        help='Quantity specifically that can be potentially manufactured with available components.'
    )
    mrp_has_bom = fields.Boolean(
        compute='_compute_mrp_potential_qty',
        string='Has Manufacturing BoM',
        help='Technical field to toggle visibility of potential qty.'
    )

    @api.depends('bom_ids', 'bom_ids.type', 'bom_ids.bom_line_ids')
    def _compute_mrp_potential_qty(self):
        for product in self:
            potential_qty = 0.0
            has_bom = False
            # Search for the most relevant BoM (standard priority used by MRP)
            bom = self.env['mrp.bom']._bom_find(product, bom_type='normal')[product]
            
            if bom and bom.type == 'normal':
                has_bom = True
                if bom.bom_line_ids:

                    # Calculate potential based on components
                    # Emulating Odoo's _compute_current_production_capacity logic from mrp_report_bom_structure
                    component_potentials = []
                    has_storable_components = False
                    
                    for line in bom.bom_line_ids:
                        # Skip if not storable (services/consumables don't restrict production in standard logic)
                        if not line.product_id.is_storable:
                            continue
                            
                        has_storable_components = True
                        qty_needed = line.product_qty
                        
                        if qty_needed <= 0:
                            continue

                        # Use Free Qty (On Hand - Reserved) to match "Ready to Produce" column logic
                        stock_available = line.product_id.free_qty
                        if stock_available < 0:
                            stock_available = 0.0
                            
                        limit = stock_available / qty_needed
                        component_potentials.append(limit)
                    
                    if has_storable_components and component_potentials:
                        # Floor down to nearest whole unit (standard interpretation, though float is valid)
                        # Report uses: float_round(..., precision_digits=0, rounding_method='DOWN')
                        import math
                        potential_qty = math.floor(min(component_potentials))
                    else:
                        potential_qty = 0.0

            product.mrp_potential_qty = potential_qty
            product.mrp_has_bom = has_bom

    def action_view_mrp_bom_structure(self):
        self.ensure_one()
        # Search for the most relevant BoM (standard priority used by MRP)
        bom = self.env['mrp.bom']._bom_find(self, bom_type='normal')[self]
        
        if bom:
            action = self.env["ir.actions.actions"]._for_xml_id("mrp.action_report_mrp_bom")
            # The client action expects active_id to be value of the BoM or Product?
            # Standard BoM form uses active_id=bom.id
            action['context'] = {
                'active_id': bom.id,
                'active_model': 'mrp.bom',
                'activate_availabilities': True
            }
            return action
        return False
