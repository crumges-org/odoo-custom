# -*- coding: utf-8 -*-
# Copyright 2024 Cybrosys Technologies Pvt. Ltd.
# Copyright 2024 Crumges
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models


class WebsiteMenu(models.Model):
    """Extend website.menu model"""
    _inherit = 'website.menu'