{
    'name': 'Crumges POS HR Category Restriction',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Restrict POS categories by employee',
    'description': """
        This module allows restricting the visible product categories in the Point of Sale 
        based on the logged-in employee.
    """,
    'author': 'Antigravity / Dimjo',
    'depends': ['crumges_pos_hr_restriction'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'crumges_pos_hr_restriction_category/static/src/app/**/*',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
