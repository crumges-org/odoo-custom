{
    "name": "Project Task: Assign Portal Users",
    "summary": "Allows assigning portal users as task assignees without granting backend access",
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "Crumges",
    "website": "https://www.crumges.com",
    "license": "LGPL-3",
    "depends": [
        "project",
    ],
    "data": [
        "views/project_task_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [],
        "web.assets_backend": [],
    },
    "description": """
This module allows assigning portal users as responsible persons in project tasks
(project.task.user_ids), even if they do not have backend access.

It is useful when working with external collaborators or clients that should be included
in the responsibility tracking of tasks, without giving them full internal user rights.
""",
    "external_dependencies": {},
    "images": ["static/description/icon.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
}


