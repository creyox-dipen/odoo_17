# -*- coding: utf-8 -*-
# Email: sales@creyox.com
{
    'name': 'Update Mass Product Accounts | Update Mass Product Income & Expense Account | Update Mass Product Accounts in Many Way',
    'version': '17.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'author': 'Creyox Technologies',
    'price': 0,
    'currency': 'USD',
    'support': 'sales@creyox.com',
    'summary': """This module allow user to mass update the product accounts.""",
    'sequence': '1',
    'description': """
            Mass Update Product Accounts.
    """,
    'depends': ['stock', 'sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/update_product_accounts_wizard.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
