{
    'name': 'cr_product_reviews',
    'version': '2.0',
    'summary': 'Product Reviews Model',
    'description': """
        Product Reviews Model
    """,
    'category': 'accounting',
    'website': '',
    'depends': ['base', 'product','stock'],
    'author': 'dipen',
    'data': [
        'security/ir.model.access.csv',
        'views/product_review.xml',
        'views/product_product.xml',
        'views/product_review_menu.xml',
        'views/product_review_report_wizard.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}