# -*- coding: utf-8 -*-
# Email: sales@creyox.com
{
    'name': 'Product Sales Report | Product Sale Report For Specific Time | Product Sale Report From POS & Sales',
    'version': '17.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'author': 'Creyox Technologies',
    'price': 0,
    'currency': 'USD',
    'support': 'sales@creyox.com',
    'summary': """This module helps user to print the report of product sales between specific time.""",
    'sequence': '1',
    'description': """
            Print the report of product sales between specific time.
    """,
    'depends': ['sale_management', 'point_of_sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_sale_report.xml',
        'views/product_sale_report_wizard.xml',
        'views/product_sale_report_template.xml',
    ],
    'images': [
        'static/description/banner.gif'
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
