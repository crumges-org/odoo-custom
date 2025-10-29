# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProjectTaskAdvanced(models.Model):
    """
    Extension of project.task to support advanced parent/child hierarchy
    for upsell operations.
    """
    _inherit = 'project.task'

    def _get_or_create_parent_task(self, sale_line, project_id, partner_id):
        """
        Find or create a parent task for a given sale order line.
        
        This method is used when creating subtasks for upsell categories that use
        parent task hierarchy. It ensures there's always a parent task to attach
        subtasks to.
        
        :param sale_line: sale.order.line record (the parent product line)
        :param project_id: project.project record (FSM project)
        :param partner_id: res.partner record (customer)
        :return: project.task record (parent task)
        """
        self.ensure_one()
        
        # Search for existing parent task
        parent_task = self.search([
            ('sale_line_id', '=', sale_line.id),
            ('parent_id', '=', False),  # Must be a parent (not a subtask)
            ('project_id', '=', project_id.id),
        ], limit=1)
        
        if parent_task:
            _logger.info(
                f"Found existing parent task {parent_task.id} for sale line {sale_line.id}"
            )
            return parent_task
        
        # Create parent task if not found
        parent_task_vals = {
            'name': sale_line.name or sale_line.product_id.name,
            'project_id': project_id.id,
            'partner_id': partner_id.id,
            'sale_line_id': sale_line.id,
            'allocated_hours': sale_line.product_uom_qty,
            'description': _(
                "Parent task for managing %(product)s operations.\n"
                "Total hours allocated: %(hours)s\n\n"
                "Subtasks will be created under this task and hours will accumulate here."
            ) % {
                'product': sale_line.product_id.name,
                'hours': sale_line.product_uom_qty,
            }
        }
        
        parent_task = self.create(parent_task_vals)
        
        _logger.info(
            f"Created parent task {parent_task.id} for sale line {sale_line.id} "
            f"with {sale_line.product_uom_qty} allocated hours"
        )
        
        return parent_task
    
    @api.model
    def _prepare_subtask_values(self, parent_task, name, description, allocated_hours, 
                                helpdesk_ticket_id=False):
        """
        Prepare values for creating a subtask under a parent task.
        
        :param parent_task: project.task record (parent)
        :param name: str (subtask name)
        :param description: str (subtask description)
        :param allocated_hours: float (hours allocated to subtask)
        :param helpdesk_ticket_id: int (optional helpdesk ticket ID)
        :return: dict (values for task creation)
        """
        vals = {
            'name': name,
            'parent_id': parent_task.id,
            'project_id': parent_task.project_id.id,
            'partner_id': parent_task.partner_id.id,
            'sale_line_id': parent_task.sale_line_id.id,  # Same as parent!
            'allocated_hours': allocated_hours,
            'description': description,
        }
        
        if helpdesk_ticket_id:
            vals['helpdesk_ticket_id'] = helpdesk_ticket_id
        
        return vals