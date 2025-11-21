# -*- coding: utf-8 -*-
# Copyright 2024 Crumges
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Project Subtask Timesheet UX',
    'version': '18.0.1.0.0',
    'category': 'Project Management',
    'website': 'https://crumges.com',
    'author': 'Crumges',
    'license': 'LGPL-3',
    'summary': 'Mejora la experiencia de usuario en hojas de tiempo de subtareas de proyecto',
    'description': '''
        Project Subtask Timesheet UX
        =============================
        
        Este módulo mejora la experiencia de usuario en la gestión de hojas de tiempo
        relacionadas con subtareas de proyectos en Odoo.
        
        Características:
        ----------------
        
        * Interfaz mejorada para el registro de tiempo en subtareas
        * Visualización optimizada de datos de tiempo
        * Mejores controles de validación
        * Experiencia de usuario más intuitiva
        
        Dependencias:
        ----------------
        
        * project: Módulo base de gestión de proyectos
        * hr_timesheet: Módulo de gestión de hojas de tiempo
    ''',
    'depends': [
        'project',
        'hr_timesheet',
    ],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}