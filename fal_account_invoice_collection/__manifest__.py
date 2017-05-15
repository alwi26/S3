# -*- coding: utf-8 -*-
{
    "name": "GEN: Account Invoice Collection",
    "version": "1.0",
    "author": "Falinwa Indonesia",
    "description": """
    Add Account Invoice Collection
    """,
    "depends": ["base", "account"],
    "init_xml": [],
    "data": [
        "wizard/fal_receipt_date_wizard_view.xml",
        "views/account_invoice_view.xml",
    ],
    "active": False,
    "application": False,
    "installable": True,
}
