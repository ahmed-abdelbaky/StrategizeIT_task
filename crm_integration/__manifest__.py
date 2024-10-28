{
    'name': 'Crm Integration',
    'Author': 'Ahmed Abd El Baky',
    "description": """
                There are URIs available:
                
                /v1/customer/auth                 POST    - Login in Odoo and set cookie s
                
                /v1/customer/create              POST     - Read all (with optional domain, fields, offset, limit, order)
                /v1/customer/update/<string:customer_id>'          PUT     - Read one (with optional fields)""",
    'depends': ['contacts'],
    'external_dependencies': {
        'python': [
            'pyjwt',
        ],
    },
    'data': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
