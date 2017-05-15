# -*- coding: utf-8 -*-
{
    "name": "Sale Package",
    "version": "1.0",
    'author': 'Falinwa Indonesia',
    "description": """
    Add sale package in sale order.
    """,
    "depends": [
        'sale',
        'account',
        'dos_amount_to_text_id'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/invoice_view.xml',
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
