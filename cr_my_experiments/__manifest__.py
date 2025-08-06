{
    'name': 'cr_my_experiment',
    'version': '1.0',
    'summary': 'cr_my_experiment',
    'description': """
        cr_my_experiment
    """,
    'category': 'accounting',
    'website': '',
    'depends': ['base',],
    'author': 'Creyox Technologies',
    'data': [
        'views/student.xml',
        'views/access_groups.xml',
        'views/teacher.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}