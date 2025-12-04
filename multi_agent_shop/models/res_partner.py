# -*- coding: utf-8 -*-
# Copyright 2024 Cybrosys Technologies Pvt. Ltd.
# Copyright 2024 Crumges
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models, fields


class ResPartner(models.Model):
    """Extend res.partner to add agent functionality"""
    _inherit = 'res.partner'

    is_agent = fields.Boolean(
        string='Es Agente',
        default=False,
        help='Marcar si este contacto es un agente de ventas'
    )
    agent_id = fields.Many2one(
        'res.partner',
        string='Agente Asignado',
        help='Agente responsable de este cliente'
    )