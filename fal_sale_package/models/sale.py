from odoo import models, api, fields, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
import math
from odoo.addons.dos_amount_to_text_id import amount_to_text_id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_gross_total = fields.Monetary(
        string='Gross Total', store=True,
        readonly=True, compute='_amount_all'
    )
    fal_disc_total = fields.Monetary(
        string='Discount Total', store=True,
        readonly=True, compute='_amount_all'
    )
    fal_additional_disc = fields.Float(string='Additional Disc')
    fal_nett_total = fields.Monetary(string='Nett Total')
    fal_amount_in_words = fields.Char(string='Amount in Words',)
    fal_sale_type = fields.Selection([
        ('project', 'Project'),
        ('retail', 'Retail'),
        ('agen', 'Agent'),
        ('package', 'Package')], string='Sale Type', default='retail')
    fal_package_id = fields.Many2one('fal.sale.package', string='Package')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        cur = False
        for order in self:
            amount_in_words = False
            free = tax_free = untax_free = 0.0
            amount_untaxed = amount_tax = gross = disc = 0.0
            if order.pricelist_id:
                cur = order.pricelist_id.currency_id
            else:
                cur = order.company_id.currency_id
            for line in order.order_line:
                if line.fal_is_free:
                    free += line.price_total
                    untax_free += line.price_subtotal
                    tax_free += line.price_tax
                gross += line.price_total
                disc += (line.price_unit * (line.discount / 100.0)) * \
                    line.product_uom_qty
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                total = amount_untaxed + amount_tax - free
                amount_in_words = amount_to_text_id.amount_to_text(
                    math.floor(total), lang='id', currency=cur.name)
            order.update({
                'fal_gross_total': cur.round(gross),
                'fal_disc_total': cur.round(disc) + free,
                'amount_untaxed': cur.round(amount_untaxed) - untax_free,
                'amount_tax': cur.round(amount_tax) - tax_free,
                'amount_total': amount_untaxed + amount_tax,
                'fal_amount_in_words': amount_in_words,
            })
        return res

    @api.multi
    def load_package(self):
        line = self.env['sale.order.line']
        for sale in self:
            if sale.state == 'draft':
                if not sale.package_id:
                    raise ValidationError(
                        _('No Package to Load.\nPlease select \
                            the package for this Order')
                    )
                if sale.order_line:
                    sale.order_line.unlink()
                if sale.package_id:
                    for x in sale.package_id.package_line_ids:
                        tax_ids = [(6, 0, [a.id for a in x.tax_id])]
                        vals = {
                            'product_id': x.product_id.id,
                            'product_uom_qty': x.product_uom_qty,
                            'product_uom': x.product_uom.id,
                            'price_unit': x.price_unit,
                            'order_id': sale.id,
                            'tax_id': tax_ids
                        }
                        line.create(vals)

            if sale.state in ['sale', 'done']:
                raise ValidationError(_('You can not add a sale order \
                    line.\nYour Order state is not in Draft'))


class SaleOrderLines(models.Model):
    _inherit = 'sale.order.line'

    fal_is_free = fields.Boolean(string='Free')


class FalSalePackage(models.Model):
    _name = 'fal.sale.package'
    _description = 'Sale Package'

    name = fields.Char(string='Package Name')
    partner_id = fields.Many2one('res.partner', string='Customer')
    package_price = fields.Float(string='Package Price')
    package_line_ids = fields.One2many(
        'fal.package.lines', 'package_id', string='Product Lines')


class FalPackageLines(models.Model):
    _name = 'fal.package.lines'
    _description = 'Sale Package Product Lines'

    package_id = fields.Many2one('fal.sale.package', string='Sale Package')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('sale_ok', '=', True)],
        change_default=True, ondelete='restrict',
        required=True
    )
    product_uom_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1.0
    )
    product_uom = fields.Many2one(
        'product.uom', string='Unit of Measure',
        required=True
    )
    price_unit = fields.Float(
        'Unit Price', required=True,
        digits=dp.get_precision('Product Price'), default=0.0
    )
    tax_id = fields.Many2many(
        'account.tax', string='Taxes',
        domain=['|', ('active', '=', False), ('active', '=', True)]
    )
