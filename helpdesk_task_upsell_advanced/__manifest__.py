# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Task Upsell Advanced',
    'version': '18.0.1.0.0',
    'summary': """
        Advanced upsell functionality with parent/child task hierarchy 
        and parent product accumulation for subscription orders
    """,
    'description': """
        This module extends helpdesk_task_upsell to provide advanced functionality:
        
        Key Features:
        =============
        * Parent/Child Task Hierarchy: Creates subtasks under a parent task
        * Parent Product Accumulation: Hours accumulate in parent product line
        * Dummy Information Lines: Informative lines that don't invoice directly
        * Automatic Parent Task Detection: Finds or creates parent tasks automatically
        * Subscription Order Integration: Seamless integration with subscription orders
        
        Use Case:
        =========
        When selling services like GPS installations (50 units), instead of creating
        50 independent tasks, this module creates:
        - 1 parent task for "GPS Installations" (50 hours)
        - Individual subtasks for each installation (1 hour each)
        - Hours from subtasks accumulate in the parent task
        - Informative lines in SO for traceability (vehicle plates, etc.)
        
        Technical:
        ==========
        - Extends upsell.category with parent_product_id and use_parent_task
        - Extends helpdesk.create.fsm.task wizard with advanced logic
        - Maintains 100% backward compatibility with base module
    """,
    'author': 'Advanced Odoo Solutions',
    'website': 'https://www.example.com',
    'category': 'Services/Helpdesk',
    'depends': [
        'helpdesk_task_upsell',  # Base module we're extending
        'project',               # For parent_id in tasks
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/upsell_category_views.xml',
        'wizards/create_task_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}