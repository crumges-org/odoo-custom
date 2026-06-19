from odoo import api, fields, models

class CommissionMakeInvoice(models.TransientModel):
    _inherit = "commission.make.invoice"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Si se requiere product_id y no está asignado todavía
        if 'product_id' in fields_list and not res.get('product_id'):
            # Intentamos buscar el producto creado en data
            product = self.env.ref('crumges_commission_invoice_product.product_commission_default', raise_if_not_found=False)
            if product:
                res['product_id'] = product.id
        return res
