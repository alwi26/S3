# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class propose_wizard(models.TransientModel):
    _name = "fal.approve.wizard"
    _description = "approve Wizard"

    fal_proposed_credit = fields.Float(string="Proposed Credit")
    fal_available_credit = fields.Float(
        string="Available Credit",
    )

    @api.multi
    def approve(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        user = self.env.user.name
        sale = self.env['sale.order'].browse(active_id)
        approve = self.env['fal.approval.userlist'].search([
            ('users_id', '=', user), ('sale_id', '=', sale.id)
        ])
        approve.write({'approved': True})

        count_approved = len(self.env['fal.approval.userlist'].search(
            [('approved', '=', True), ('sale_id', '=', sale.id)]
        ))
        count_user = len(self.env['fal.approval.userlist'].search([
            ('sale_id', '=', sale.id)
        ]))
        if count_approved == count_user or count_user == 0:
            sale.write({
                'fal_proposal_approved': True,
                'fal_additional_credit': self.fal_proposed_credit,
                'state': 'approved'})

        if approve.id is False:
            msg = 'You are not listed as approval user'
            raise ValidationError(_(msg))
