{
    'name': 'Gestión de Partes de Horas en Portal',
    'summary': 'Permite a usuarios de portal gestionar sus partes de horas',
    'version': '18.0.1.0.0',
    'category': 'Services/Timesheets',
    'website': 'https://crumges.com',
    'author': 'Crumges',
    'maintainers': ['Crumges'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        "portal",
        "hr_timesheet",
        "project",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
    ],
    'assets': {},
    'images': ['static/description/icon.png'],
}
