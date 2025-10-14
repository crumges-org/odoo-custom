# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subscription_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Linked Subscription Product',
        domain=[('recurring_invoice', '=', True)],
        help='The subscription product whose quantity will be automatically adjusted '
             'when this service product is delivered. '
             'Example: Link "GPS Installation" to "GPS Monthly Subscription"',
        copy=False,
    )
    
    subscription_service_type = fields.Selection(
        selection=[
            ('installation', 'Installation Service'),
            ('uninstallation', 'Uninstallation Service'),
        ],
        string='Subscription Service Type',
        help='Defines if this service increases (installation) or decreases (uninstallation) '
             'the subscription quantity.',
    )

    @api.constrains('subscription_product_id', 'subscription_service_type')
    def _check_subscription_service_type(self):
        """Ensure that if a subscription is linked, service type is defined."""
        for record in self:
            if record.subscription_product_id and not record.subscription_service_type:
                raise ValidationError(_(
                    'Product "%s" has a linked subscription product but no service type defined. '
                    'Please specify if this is an Installation or Uninstallation service.'
                ) % record.name)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    subscription_product_id = fields.Many2one(
        comodel_name='product.product',
        related='product_tmpl_id.subscription_product_id',
        string='Linked Subscription Product',
        readonly=False,
        store=True,
    )
    
    subscription_service_type = fields.Selection(
        related='product_tmpl_id.subscription_service_type',
        string='Subscription Service Type',
        readonly=False,
        store=True,
    )