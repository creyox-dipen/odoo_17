{
    'name': 'my_hooks',
    'version': '1.0',
    'summary': '',
    'description': """

    """,

    'category': 'accounting',
    'website': '',
    'depends': ['base'],
    'data': [

    ],
    'demo': [

    ],
    'images': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

    'pre_init_hook' : 'my_pre_init_hook',
    'post_init_hook' : 'my_post_init_hook',
    'uninstall_hook' : 'my_uninstall_hook',
    'post_load_hook' : 'my_post_load_hook'
}