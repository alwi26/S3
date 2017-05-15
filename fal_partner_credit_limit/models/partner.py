# -*- coding:utf-8 -*-
from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    fal_warning_type = fields.Selection([
        ('none', 'None'),
        ('blocked', 'Block'),
        ('value', 'Value')
    ], string='Sale Restriction')
