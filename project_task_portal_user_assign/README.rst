===============================
Project Task Portal User Assign
===============================

This module allows you to assign *portal users* as task assignees in **Project Tasks** (`project.task.user_ids`), which is not allowed by default in Odoo.

By default, the task's assignee field (`user_ids`) is limited to internal users only. This module removes that restriction so that you can:

- Assign portal users as responsible persons in project tasks.
- Maintain visibility of responsibilities for reporting or process tracking.
- Avoid giving backend access to portal users.

This is useful when portal users participate in project tasks externally (e.g. external contractors, collaborators, clients) but do **not need backend access**.

Usage
=====

1. Install this module.
2. In the task form, you will be able to assign any portal user as a task assignee.
3. Portal users will not gain backend access or visibility, but you can include them in task responsibilities and generate reports accordingly.

This module does **not** depend on ``portal_backend`` and does **not** change user permissions.

Credits
=======

Authors
~~~~~~~
* Crumges

Maintainers
~~~~~~~~~~~
This module is maintained by Crumges.

License
=======
LGPL-3
