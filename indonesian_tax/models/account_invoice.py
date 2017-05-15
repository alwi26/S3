# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'invoice_line_ids.price_subtotal',
        'tax_line_ids.amount', 'currency_id',
        'company_id', 'date_invoice')
    def _compute_amount(self):
        self.gross = sum(
            (line.price_unit * line.quantity) for line in self.invoice_line_ids
        )
        self.disc_total = sum(
            (line.price_unit * line.quantity * line.discount / 100.0)
            for line in self.invoice_line_ids
        )
        return super(AccountInvoice, self)._compute_amount()

    npwp = fields.Char(string='NPWP')
    gross = fields.Monetary(
        string='Gross Total',
        store=True, readonly=True, compute='_compute_amount')
    disc_total = fields.Monetary(
        string='Discount',
        store=True, readonly=True, compute='_compute_amount')
    nomor_faktur_pajak = fields.Char(string='Nomor Faktur Pajak', size=16)
    faktur_pajak_id = fields.Many2one('faktur.pajak', string='Faktur Pajak')
    invoice_receipt_date = fields.Date('Date Invoice Receipt')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id.npwp:
            self.npwp = self.partner_id.npwp
        return res

    @api.multi
    def action_create_faktur(self):
        faktur_obj = self.env['faktur.pajak']
        today = fields.Date.context_today(self)

        for inv in self:
            if inv.type == 'out_invoice' and inv.faktur_pajak_id:
                vals = {
                    'date_used': today,
                    'invoice_id': inv.id,
                    'partner_id': inv.partner_id.id,
                    'pajak_type': 'out',
                    'dpp': inv.amount_untaxed or 0.0,
                    'tax_amount': inv.amount_tax or 0.0,
                    'currency_id': inv.currency_id.id,
                    'state': '1',
                }
                inv.faktur_pajak_id.write(vals)
            if inv.type == 'in_invoice':
                if inv.nomor_faktur_pajak:
                    kode_pt = inv.nomor_faktur_pajak[:3]
                    tahun = inv.nomor_faktur_pajak[4:6]
                    nomor_fp = inv.nomor_faktur_pajak[-8:]
                    vals = {
                        'date_used': today,
                        'invoice_id': inv.id,
                        'partner_id': inv.partner_id.id,
                        'pajak_type': 'in',
                        'dpp': inv.amount_untaxed or 0.0,
                        'tax_amount': inv.amount_tax or 0.0,
                        'currency_id': inv.currency_id.id,
                        'state': '1',
                        'nomor_perusahaan': kode_pt,
                        'tahun_penerbit': tahun,
                        'nomor_urut': nomor_fp,
                    }
                    faktur_obj.create(vals)

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for inv in self:
            inv.action_create_faktur()
        return res
