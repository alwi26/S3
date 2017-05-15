from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_check = fields.Boolean(compute="_fal_check")

    @api.multi
    def action_invoice_paid(self):
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_(
                'Invoice must be validated in \
                    order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_(
                'You cannot pay an invoice which is partially paid. \
                    You need to reconcile payment entries first.'))
        return False

    @api.depends('residual')
    def _fal_check(self):
        for inv in self:
            if inv.residual == 0:
                inv.fal_check = True

    @api.multi
    def action_paid(self):
        for inv in self:
            inv.write({'state': 'paid'})
