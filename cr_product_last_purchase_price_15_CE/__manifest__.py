{
    'name': 'Product Last Purchase Price',
    'version': '1.0',
    'summary': 'Product Last Purchase Price',
    'description': """
        This module finds the last purchase price
    """,
    'category': 'accounting',
    'website': '',
    'depends': ['base', 'purchase', 'product', ],
    'author': 'Creyox Technology',
    'data': [
        'views/product_product.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

    'post_init_hook' : 'my_post_init_hook',
}
