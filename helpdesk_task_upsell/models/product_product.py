# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.product'
    
    is_reparation = fields.Boolean(string='Is a reparation', default=False)
    is_installation = fields.Boolean(string='Is a installation', default=False)
    is_uninstallation = fields.Boolean(string='Is a uninstallation', default=False)
