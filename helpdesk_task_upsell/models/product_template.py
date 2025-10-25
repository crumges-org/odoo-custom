# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_reparation = fields.Boolean(string='Is a reparation', default=False)
    is_installation = fields.Boolean(string='Is a installation', default=False)
    is_uninstallation = fields.Boolean(string='Is a uninstallation', default=False)
    
    @api.constrains('is_reparation', 'is_installation', 'is_uninstallation')
    def _check_is_reparation_installation_uninstallation(self):
        for product in self:
            if product.is_reparation and product.is_installation:
                raise ValidationError(_('You can not set a reparation and an installation at the same time.'))
            if product.is_reparation and product.is_uninstallation:
                raise ValidationError(_('You can not set a reparation and an uninstallation at the same time.'))
            if product.is_installation and product.is_uninstallation:
                raise ValidationError(_('You can not set an installation and an uninstallation at the same time.'))
