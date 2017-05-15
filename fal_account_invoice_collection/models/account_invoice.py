from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_receipt_date = fields.Date(string='Receipt Date')

    @api.onchange('fal_receipt_date')
    def onchange_date(self):
        if self.fal_receipt_date:
            self.date_due = self.fal_receipt_date

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        # Override the original version
        if self.fal_receipt_date:
            self.date_due = self.fal_receipt_date

    @api.multi
    def action_invoice_open(self):
        for inv in self:
            if not inv.fal_receipt_date:
                raise UserError(
                    _('Please fill Receipt Date before validation!'))
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_open_fal_receipt_date(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.receipt.date.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
