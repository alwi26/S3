# -*- coding: utf-8 -*-
from odoo import models, fields, api


class propose_wizard(models.TransientModel):
    _name = "fal.propose.wizard"
    _description = "Propose Wizard"

    fal_additional_credit = fields.Float('Additional Credit')

    @api.multi
    def propose(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        res = self.env['sale.order'].browse(active_id)
        res.write({
            'fal_proposed_credit': self.fal_additional_credit,
            'state': 'waiting'})
