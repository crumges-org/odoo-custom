# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class UpsellCategory(models.Model):
    _name = 'upsell.category'
    _description = 'Upsell Category'

    name = fields.Char('Name', required=True, unique=True)
    product_id = fields.Many2one('product.product', 'Product', required=False)

    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        result = super(UpsellCategory, self).create(values)
        for row in result:
            product = self.env['product.product'].create(
                {
                    'name': row.name,
                    'type': 'service',
                    'service_tracking': 'task_global_project',
                    'service_policy': 'delivered_timesheet',
                    'project_id': self.env.ref('industry_fsm.fsm_project').id,
                    'is_upsell': True,
                }
            )
            row.write({'product_id': product.id})
        return result
