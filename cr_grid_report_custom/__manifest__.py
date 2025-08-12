# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

{
    'name': 'cr_grid_report_custom',
    'version': '17.0',
    'summary': 'cr_grid_report_custom',
    'description': """
        cr_grid_report_custom
    """,
    'category': 'accounting',
    'website': '',
    'depends': ['base', 'sale', 'product_matrix', 'sale_product_matrix'],
    'author': 'Creyox Technology',
    'data': [
        'security/ir.model.access.csv',
        'views/order_matrix.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}