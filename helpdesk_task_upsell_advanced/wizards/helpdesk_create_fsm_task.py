# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HelpdeskCreateFSMTaskAdvanced(models.TransientModel):
    """
    Advanced extension of helpdesk.create.fsm.task wizard.
    
    Implements the parent/child task hierarchy logic when use_parent_task
    is enabled in the selected upsell category.
    """
    _inherit = 'helpdesk.create.fsm.task'

    def action_generate_task(self):
        """
        Override to implement advanced task generation logic.
        
        FLOW:
        =====
        1. Check if category uses parent task hierarchy
        2. If NO → Call super() (standard behavior from base module)
        3. If YES → Execute advanced logic:
           a. Find or create parent product line in subscription order
           b. Find or create parent task
           c. Create subtask under parent task
           d. Create informative dummy line
           e. Link everything correctly
        """
        self.ensure_one()
        
        # Check if we should use advanced logic
        if not (self.for_upsell and self.upsell_category_id.use_parent_task):
            # Standard behavior - call base module logic
            _logger.info(
                f"Using standard task creation for ticket {self.helpdesk_ticket_id.id}"
            )
            return super(HelpdeskCreateFSMTaskAdvanced, self).action_generate_task()
        
        # ADVANCED LOGIC: Parent/Child Task Hierarchy
        _logger.info(
            f"Using advanced parent/child task creation for ticket {self.helpdesk_ticket_id.id} "
            f"with category {self.upsell_category_id.name}"
        )
        
        # Validate required fields
        self._validate_advanced_fields()
        
        # Step 1: Get or create parent product line in subscription order
        parent_line = self._get_or_create_parent_line()
        
        # Step 2: Get or create parent task
        parent_task = self._get_or_create_parent_task(parent_line)
        
        # Step 3: Create subtask under parent task
        subtask = self._create_subtask(parent_task)
        
        # Step 4: Create informative dummy line
        self._create_informative_line(subtask)
        
        # Step 5: Update helpdesk ticket (optional - commented in base module)
        # self._update_ticket_info()
        
        _logger.info(
            f"Successfully created subtask {subtask.id} under parent task {parent_task.id} "
            f"for category {self.upsell_category_id.name}"
        )
        
        return subtask

    def _validate_advanced_fields(self):
        """Validate that all required fields for advanced logic are present."""
        if not self.upsell_category_id.parent_product_id:
            raise ValidationError(_(
                "The category '%(category)s' is configured to use parent task hierarchy "
                "but does not have a 'Parent Product' configured.\n\n"
                "Please configure the parent product in the category settings."
            ) % {'category': self.upsell_category_id.name})
        
        if not self.subsription_id:
            raise ValidationError(_(
                "A subscription order is required for advanced upsell operations."
            ))
        
        if self.subsription_id.state != 'sale':
            raise ValidationError(_(
                "The subscription order must be confirmed (state: 'sale') "
                "to create upsell tasks.\n\n"
                "Current state: %(state)s"
            ) % {'state': self.subsription_id.state})

    def _get_or_create_parent_line(self):
        """
        Find or create the parent product line in the subscription order.
        
        The parent line is where hours will accumulate and be invoiced.
        
        :return: sale.order.line record
        """
        parent_product = self.upsell_category_id.parent_product_id
        
        # Search for existing line with parent product
        parent_line = self.env['sale.order.line'].search([
            ('order_id', '=', self.subsription_id.id),
            ('product_id', '=', parent_product.id),
        ], limit=1)
        
        if parent_line:
            _logger.info(
                f"Found existing parent line {parent_line.id} for product "
                f"{parent_product.name} in SO {self.subsription_id.name}"
            )
            return parent_line
        
        # Create new parent line if not found
        parent_line_vals = {
            'order_id': self.subsription_id.id,
            'product_id': parent_product.id,
            'product_uom_qty': self.qty,  # Initial quantity
            'name': parent_product.name,
            'project_id': parent_product.project_id.id,
        }
        
        parent_line = self.env['sale.order.line'].create(parent_line_vals)
        
        _logger.info(
            f"Created parent line {parent_line.id} for product {parent_product.name} "
            f"in SO {self.subsription_id.name} with {self.qty} hours"
        )
        
        return parent_line

    def _get_or_create_parent_task(self, parent_line):
        """
        Find or create the parent task associated with the parent line.
        
        :param parent_line: sale.order.line record
        :return: project.task record
        """
        # Use the helper method from project.task extension
        parent_task = self.env['project.task']._get_or_create_parent_task(
            sale_line=parent_line,
            project_id=self.project_id,
            partner_id=self.partner_id
        )
        
        return parent_task

    def _create_subtask(self, parent_task):
        """
        Create a subtask under the parent task.
        
        This subtask represents the individual operation (e.g., one installation).
        Hours logged here will accumulate in the parent task's sale_line_id.
        
        :param parent_task: project.task record
        :return: project.task record (the created subtask)
        """
        # Prepare subtask name
        subtask_name = f"{self.name} - {self.upsell_category_id.name}: {self.task_description}"
        
        # Prepare subtask description
        subtask_description = _(
            "%(category)s Operation\n"
            "Description: %(description)s\n"
            "Allocated Hours: %(hours)s\n\n"
            "Related Ticket: %(ticket)s\n"
            "Customer: %(customer)s\n\n"
            "NOTE: This is a subtask. Hours logged here will accumulate in the parent task "
            "and be invoiced through the parent product line."
        ) % {
            'category': self.upsell_category_id.name,
            'description': self.task_description,
            'hours': self.qty,
            'ticket': self.helpdesk_ticket_id.name if self.helpdesk_ticket_id else 'N/A',
            'customer': self.partner_id.name,
        }
        
        # Prepare subtask values using helper method
        subtask_vals = self.env['project.task']._prepare_subtask_values(
            parent_task=parent_task,
            name=subtask_name,
            description=subtask_description,
            allocated_hours=self.qty,
            helpdesk_ticket_id=self.helpdesk_ticket_id.id if self.helpdesk_ticket_id else False
        )
        
        # Create subtask
        subtask = self.env['project.task'].create(subtask_vals)
        
        _logger.info(
            f"Created subtask {subtask.id} '{subtask.name}' under parent task {parent_task.id}"
        )
        
        return subtask

    def _create_informative_line(self, subtask):
        """
        Create an informative (dummy) line in the subscription order.
        
        This line is for traceability and customer information only.
        It should NOT invoice independently - it's just to show the detail
        of operations performed.
        
        :param subtask: project.task record
        """
        dummy_product = self.upsell_category_id.product_id
        
        # Prepare informative line values
        line_vals = {
            'order_id': self.subsription_id.id,
            'product_id': dummy_product.id,
            'product_uom_qty': 0,  # Zero quantity - won't invoice
            'qty_delivered': 0,
            'name': f"{self.upsell_category_id.name}: {self.task_description}",
            'price_unit': 0,  # Zero price
            'task_id': subtask.id,  # Link to subtask for reference
        }
        
        # Create informative line
        info_line = self.env['sale.order.line'].create(line_vals)
        
        _logger.info(
            f"Created informative line {info_line.id} for subtask {subtask.id} "
            f"with zero quantity (dummy line for traceability)"
        )
        
        return info_line

    def _update_ticket_info(self):
        """
        Optionally update the helpdesk ticket with upsell information.
        
        NOTE: This is commented out in the base module, so keeping it optional here.
        """
        if self.helpdesk_ticket_id:
            self.helpdesk_ticket_id.write({
                'for_upsell': True,
                'upsell_category_id': self.upsell_category_id.id,
                'subsription_id': self.subsription_id.id,
            })
            _logger.info(
                f"Updated ticket {self.helpdesk_ticket_id.id} with upsell information"
            )