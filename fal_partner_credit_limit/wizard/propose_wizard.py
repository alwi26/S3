# -*- coding: utf-8 -*-
from odoo import models, api


class propose_wizard(models.TransientModel):
    _name = "propose.wizard"
    _description = "Propose Wizard"

    @api.multi
    def propose(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        res = self.env['sale.order'].browse(active_id)
        res.write({
            'state': 'waiting'})
