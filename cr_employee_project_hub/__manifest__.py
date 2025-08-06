{
    'name': 'cr_employee_project_hub',
    'version': '1.0',
    'summary': 'cr_employee_project_hub',
    'description': """
        cr_employee_project_hub
    """,
    'category': 'accounting',
    'website': '',
    'depends': ['base', 'hr_holidays', 'hr', 'project'],
    'author': 'dipen',
    'data': [
        'views/employee_assign_wiz.xml',
        'views/employee_training.xml',
        'views/training_session.xml',
        'views/employee_menus.xml',
        'views/access_groups.xml',
        'views/project_task.xml',
        'views/hr_employee.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}