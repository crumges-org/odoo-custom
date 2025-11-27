{
    'name': 'Project Subtask Timesheet UX',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Mejoras de UX para registro automático de timesheets en subtareas',
    'depends': ['project', 'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/views/project_task_cancel_wizard_views.xml',
        'wizards/views/project_task_reopen_wizard_views.xml',
        'wizards/views/project_task_complete_wizard_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
}