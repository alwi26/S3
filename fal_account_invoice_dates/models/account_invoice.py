from odoo import fields, models, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_paid_date = fields.Date(string='Paid date', copy=False)
    fal_due_age = fields.Integer(string='Due Age', compute='_due_age')

    @api.multi
    def action_invoice_paid(self):
        res = super(AccountInvoice, self).action_invoice_paid()
        self.write(
            {'fal_paid_date': fields.Date.context_today(self)}
        )
        return res

    @api.depends('date_due')
    def _due_age(self):
        today = datetime.today().strftime('%Y-%m-%d')
        for inv in self:
            duration = 0
            if inv.date_due and inv.state != 'paid':
                duration = float(
                    (datetime.strptime(
                        today, DEFAULT_SERVER_DATE_FORMAT
                    ) - datetime.strptime(
                        inv.date_due, DEFAULT_SERVER_DATE_FORMAT
                    )).days)
                inv.fal_due_age = duration
                if duration < 0:
                    inv.fal_due_age = 0
