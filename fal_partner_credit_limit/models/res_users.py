from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    fal_user_approval = fields.Boolean(
        string="This is user approval"
    )
