from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FalReceiptDate(models.TransientModel):
    _name = 'fal.receipt.date.wizard'

    date = fields.Date(string='Receipt Date')

    @api.multi
    def assign_receipt_date(self):
        ctx = self._context
        for item in self:
            inv = self.env['account.invoice'].browse(
                ctx.get('active_id', False))
            if inv:
                inv.write({
                    'fal_receipt_date': item.date,
                    'date_due': item.date,
                })
            else:
                raise UserError(
                    _('No customer invoice found!'))
