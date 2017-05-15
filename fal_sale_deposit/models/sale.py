from odoo import api, fields, models


class FalSaleDeposit(models.Model):
    _name = 'fal.sale.deposit'
    _description = 'Sale Deposit'

    @api.depends('sale_ids.amount_total')
    def _compute_total(self):
        self.dp_settlement = sum((line.amount_total) for line in self.sale_ids)
        self.dp_on_sale = sum((line.amount_total) for line in self.sale_ids)
        self.dp_balance = self.dp_amount - self.dp_settlement

    name = fields.Char(
        string='Deposit Name',
        required=True,
    )
    partner_id = fields.Many2one('res.partner', string='Customer')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id'
    )
    dp_account = fields.Many2one('account.account', string='Deposit Account')
    dp_amount = fields.Float(string='Deposit Amount')
    dp_on_sale = fields.Float(
        string='Deposit on SO', compute='_compute_total',
        store=True
    )
    dp_settlement = fields.Float(
        string='Settlement Amount',
        compute='_compute_total', store=True
    )
    dp_balance = fields.Float(
        string='Balance', compute='_compute_total',
        store=True
    )
    sale_ids = fields.One2many(
        'sale.order', 'fal_deposit_id',
        string='Sale Order'
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get()
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_deposit_id = fields.Many2one(
        'fal.sale.deposit', string='Deposit')
