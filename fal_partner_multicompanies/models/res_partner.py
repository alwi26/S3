from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    fal_child_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Children Companies',
        domain=[('is_company', '=', True)]
    )
