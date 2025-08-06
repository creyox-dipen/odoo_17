{
    'name' : 'cr_department_management',
    'version' : '1.0',
    'summary' : '',
    'description' : """
    
    """,

    'category' : 'accounting',
    'website' : '',
    'depends' : ['base', 'mail', 'sale'],
    'data' : [
        'views/access_groups.xml',
        'security/ir.model.access.csv',
        'views/department.xml',
        'views/employee.xml',
        'views/student.xml',
        'views/department_conf.xml',
        'views/sale_order_line.xml',
        'views/split_sale.xml',
    ],
    'demo' : [],
    'images' : [],
    'installable' : True,
    'application' : True,
    'license' : 'LGPL-3',

}