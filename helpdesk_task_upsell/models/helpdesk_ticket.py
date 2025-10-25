# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    for_upsell = fields.Boolean(string='For Upsell', default=False)
    upsell_type = fields.Selection([('instalation', 'Installation'),
                                    ('uninstallation', 'Uninstallation'),
                                    ('reaparition', 'Reaparition'),
                                    ])
    
    subsription_id = fields.Many2one('sale.order', string='ClientSubscription')