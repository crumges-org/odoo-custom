# -*- coding: utf-8 -*-

from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_template = fields.Boolean(
        string='Is Template',
        default=False,
        help='If set, this task can be selected as a template when converting tickets to tasks.'
    )
