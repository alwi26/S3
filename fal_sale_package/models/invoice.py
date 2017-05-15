from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_additional_disc = fields.Float(string='Additional Disc')
    fal_nett_total = fields.Monetary(string='Nett Total')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['fal_additional_disc'] = self.fal_additional_disc
        res['fal_nett_total'] = self.fal_nett_total
        return res
