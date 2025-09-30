# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    parent_id = fields.Many2one(
        'helpdesk.ticket', 'Parent Ticket', help="Parent Ticket")
    child_ids = fields.One2many('helpdesk.ticket',
                                'parent_id', 'Child Tickets'
                                )

    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Partner",
                                 compute='_compute_partner_id',
                                 store=True,
                                 readonly=False,
                                 tracking=True, index=True
                                 )

    @api.depends('parent_id.partner_id', 'partner_id')
    def _compute_partner_id(self):
        for record in self:
            record.partner_id = record.parent_id.partner_id if \
                record.parent_id else record.partner_id
