# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ExtraInformationCategory(models.Model):
    _name = 'extra.information.category'
    _description = 'ExtraInformationCategory'

    _rec_name = 'name'
    name = fields.Char('Name', default="/")
