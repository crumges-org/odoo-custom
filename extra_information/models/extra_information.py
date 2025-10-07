# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ExtraInformation(models.Model):
    _name = 'extra.information'
    _description = 'Extra Information'

    name = fields.Char('Name', default="/")

    label = fields.Char('Label', default="/")

    value = fields.Char('Value',
                        compute='_compute_value',
                        store=True,
                        readonly=False,
                                )
    
    category_information_id = fields.Many2one(
        string='Label Category',
        comodel_name='extra.information.category',
        required=False
    )
    
    @api.depends('from_extra_information',
                 'from_contact',
                 'contact_id',
                 'category_information_id',
                 'partner_id_number_id')
    def _compute_value(self):
        for record in self:
            if record.from_extra_information:
                record.value = record.partner_id_number_id.name
                record.label = record.partner_id_number_id.category_id.name \
                    if record.partner_id_number_id.category_id \
                    else record.label
            elif record.from_contact and record.contact_id:
                record.value = record.contact_id.name
                record.label = record.category_information_id.name \
                    if record.category_information_id else record.label
            else:
                record.value = record.value

    from_contact = fields.Boolean('From Contact', default=False)

    from_extra_information = fields.Boolean(
        'Contact Extra Information', default=False)

    contact_id = fields.Many2one('res.partner', 'From Contact')

    category_id = fields.Many2one(
        string="Category",
        required=False,
        comodel_name="res.partner.id_category",
        help="ID type defined in configuration. For example, Driver License",
    )

    partner_id_number_id = fields.Many2one(
        string='Partner ID Number',
        comodel_name='res.partner.id_number',
        ondelete='restrict',
        help='Partner ID Number',
    )
