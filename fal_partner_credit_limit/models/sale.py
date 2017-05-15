# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved')
    ])
    fal_warning_type = fields.Selection(
        related="partner_id.fal_warning_type",
        string="Sale Restriction"
    )
    fal_additional_credit = fields.Float(string="Additional Credit")
    fal_proposed_credit = fields.Float(string="Proposed Credit")
    fal_proposal_approved = fields.Boolean(
        string="Proposal Approved", copy=False)
    fal_available_credit = fields.Float(
        string="Available Credit",
        compute='_available_credit'
    )
    fal_check = fields.Boolean(compute="_fal_check")

    fal_approval_user_list_ids = fields.One2many(
        'fal.approval.userlist', 'sale_id',
        string='Approval User List'
    )

    @api.multi
    def action_propose(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.propose.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.depends(
        'partner_id.credit_limit',
        'partner_id.credit',
        'fal_additional_credit'
    )
    def _available_credit(self):
        for sale in self:
            sale.fal_available_credit = \
                self.partner_id.credit_limit - \
                self.partner_id.credit + self.fal_additional_credit

    @api.depends(
        'fal_available_credit',
        'amount_total',
        'partner_id.fal_warning_type'
    )
    def _fal_check(self):
        for sale in self:
            if sale.fal_available_credit > sale.amount_total \
                    or sale.partner_id.fal_warning_type in ['blocked', 'none']:
                sale.fal_check = True

    @api.multi
    def action_approve(self):
        context = {
            'default_fal_proposed_credit': self.fal_proposed_credit,
            'default_fal_available_credit': self.fal_available_credit
        }
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.approve.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    @api.multi
    def check_credit_limit(self):
        for sale in self:
            if sale.partner_id.fal_warning_type == 'blocked':
                msg = 'This partner is Blocked.'
                raise ValidationError(_(msg))
            elif sale.partner_id.fal_warning_type == 'value':
                if sale.amount_total > sale.fal_available_credit:
                    msg = 'Can not continue because \
                        available credit is not enough.'
                    raise ValidationError(_(msg))

    @api.multi
    def action_confirm(self):
        for item in self:
            item.check_credit_limit()
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_quotation_send(self):
        for item in self:
            item.check_credit_limit()
        return super(SaleOrder, self).action_quotation_send()

    @api.model
    def create(self, vals):
        users = self.env['res.users'].search([
            ('fal_user_approval', '=', True)
        ])
        data = []
        for user in users:
            data.append((0, 0, {'users_id': user.id, 'approved': False}))
        vals["fal_approval_user_list_ids"] = data
        res = super(SaleOrder, self).create(vals)
        return res


class FalApprovalUserList(models.Model):
    _name = 'fal.approval.userlist'

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    users_id = fields.Many2one('res.users', string='User')
    approved = fields.Boolean(string="Approved")
