# -*- coding: utf-8 -*-
{
    'name': 'Sales Deposit',
    'version': '1.0',
    'author': 'Falinwa Indonesia',
    'description': '''
    Add deposit for sales order.
    ''',
    'depends': [
        'sale',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
