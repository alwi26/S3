# -*- coding: utf-8 -*-
{
    "name": "Partner Credit Limit",
    "version": "10.0",
    "description": """Partner Credit Limit
    """,
    "author": 'Falinwa Indonesia',
    "license": 'AGPL-3',
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_view.xml",
        "views/sale_view.xml",
        "views/res_users_view.xml",
        "wizard/propose_wizard.xml",
        "wizard/approve_wizard.xml",
    ],
    "installable": True,
}
