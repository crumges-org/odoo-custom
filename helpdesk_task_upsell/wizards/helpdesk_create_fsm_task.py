# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'
    _description = _('HelpdeskTicketConvertWizard')

    for_upsell = fields.Boolean(string='For Upsell', default=False)
    # upsell_type = fields.Selection([('instalation', 'Installation'),
    #                                 ('uninstallation', 'Uninstallation'),
    #                                 ('reparation', 'Reparation'),
    #                                 ])
    upsell_category_id = fields.Many2one(
        'upsell.category', string='Upsell Category')
    subsription_id = fields.Many2one('sale.order', string='Subscription')
    task_description = fields.Text(string='Task Description')

    qty = fields.Integer("Quantity", default=1)

    def action_generate_task(self):
        self.ensure_one()
        task = super(HelpdeskTicketConvertWizard, self).action_generate_task()
        # create sale order line for the task
        if self.for_upsell:
            product = self.upsell_category_id.product_id

            line = self.env['sale.order.line'].create(
                {
                    'product_id': product.product_variant_id.id,
                    'product_uom_qty': self.qty,
                    'name': f"{self.upsell_category_id.name}:{self.task_description}",
                    'order_id': self.subsription_id.id,
                    'project_id': product.project_id.id,
                    'task_id': task.id,
                }
            )
            self.subsription_id.write({'order_line': [(4, line.id)]})
            task.write(
                {
                    'sale_line_id': line.id,
                    'allocated_hours': self.qty,
                    'description': f"{self.upsell_category_id.name}: {self.task_description}",
                    'name': f"{task.name} - {self.upsell_category_id.name}: {self.task_description}"
                })
            # self.helpdesk_ticket_id.write({
            #     "for_upsell": True,
            #     "upsell_category_id": self.upsell_category_id.id,
            #     "subsription_id": self.subsription_id.id,
            # })

        return task

    def _generate_task_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            'helpdesk_ticket_id': self.helpdesk_ticket_id.id,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'description': self.helpdesk_ticket_id.description,
        }
