# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class UpsellCategoryAdvanced(models.Model):
    """
    Extension of upsell.category to support parent/child product hierarchy.
    
    This allows categories to:
    - Have a dummy/informative product (existing product_id)
    - Have a parent product where hours accumulate (new parent_product_id)
    - Enable advanced task hierarchy behavior (new use_parent_task)
    """
    _inherit = 'upsell.category'

    use_parent_task = fields.Boolean(
        string='Use Parent Task Hierarchy',
        default=False,
        help="""When enabled, this category will:
        1. Create subtasks under a parent task (not independent tasks)
        2. Use parent_product_id for hour accumulation
        3. Create informative lines in SO with product_id (no invoicing)
        4. Automatically find or create the parent task in the subscription order
        
        Use Case: For services sold in bulk (e.g., 50 GPS installations) where 
        you want individual operations as subtasks but hours accumulating in the 
        parent product line.
        """
    )
    
    parent_product_id = fields.Many2one(
        'product.product',
        string='Parent Product (Hour Accumulator)',
        domain=[('is_upsell', '=', False), ('type', '=', 'service')],
        help="""Product where hours will actually accumulate and be invoiced.
        This should be the main service product sold in the subscription 
        (e.g., 'GPS Installations' with 50 hours).
        
        When a task is created:
        - The wizard will search for this product in the subscription order
        - If found, it will use its parent task
        - If not found, it will create a new line with this product
        - Subtasks will log hours against this product's line
        """
    )
    
    @api.constrains('use_parent_task', 'parent_product_id')
    def _check_parent_product_required(self):
        """Validate that parent_product_id is set when use_parent_task is enabled."""
        for record in self:
            if record.use_parent_task and not record.parent_product_id:
                raise ValidationError(_(
                    "When 'Use Parent Task Hierarchy' is enabled, "
                    "you must specify a 'Parent Product (Hour Accumulator)'.\n\n"
                    "This is the product where hours will accumulate and be invoiced."
                ))
    
    @api.constrains('parent_product_id', 'product_id')
    def _check_different_products(self):
        """Ensure parent_product_id and product_id are different."""
        for record in self:
            if record.use_parent_task and record.parent_product_id == record.product_id:
                raise ValidationError(_(
                    "The 'Parent Product' and the 'Product' (dummy/informative) "
                    "must be different.\n\n"
                    "- Product: Used for informative lines (e.g., 'Installation: ABC-123')\n"
                    "- Parent Product: Used for hour accumulation and invoicing "
                    "(e.g., 'GPS Installations - 50 hours')"
                ))
    
    @api.onchange('use_parent_task')
    def _onchange_use_parent_task(self):
        """Clear parent_product_id when disabling use_parent_task."""
        if not self.use_parent_task:
            self.parent_product_id = False