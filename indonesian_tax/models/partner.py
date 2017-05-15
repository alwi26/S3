from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    npwp = fields.Char(string='NPWP')
