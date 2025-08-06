{
    'name': 'product_management',
    'version': '1.0',
    'summary': 'Product Management',
    'description': """
        This is product management module that handles all kind of products
    """,
    'category': 'accounting',
    'website': '',
    'authro': 'Dipen',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/category.xml',
        'views/product.xml',
        'views/supplier.xml'
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}