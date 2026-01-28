{
    'name': 'Helpdesk Task Template',
    'version': '18.0.1.0.0',
    'summary': 'Create tasks from tickets using existing tasks as templates',
    'description': """
        This module allows users to select an existing task as a template when converting a Helpdesk Ticket into a Task.
        The system will copy the template's structure (tags, type, subtasks, planned hours) while using the ticket's client and description.
    """,
    'category': 'Services/Helpdesk',
    'author': 'Crumges',
    'depends': ['project', 'helpdesk', 'project_helpdesk', 'helpdesk_fsm'],
    'data': [
        'views/project_task_views.xml',
        'views/helpdesk_ticket_convert_wizard_views.xml',
        'views/create_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
}
