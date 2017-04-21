# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import timedelta, datetime


class res_partner(models.Model):
    _inherit = 'res.partner'

    def update_cron_warning_type(self):
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([('warning_type', '!=', False),'|', ('property_payment_term_id', '=', False),('property_payment_term_id.name', 'not ilike', 'Immediate')])
        for partner_id in partner_obj.browse(partner_ids):
            self.env.cr.execute("update res_partner set warning_type='all' where id = "+str(partner_id.id))
        return True

    warning_type = fields.Selection([('none', 'None'),('blocked', 'Block'), ('value', 'Value'), ('date', 'Date'), ('all', 'Everybody')], string='Notice', required=True,  copy=False, default='all')
    credit_limit = fields.Float(string="Credit Limit", copy=False)
    credit_limit_days = fields.Integer(string="Days in Credit Limit", copy=False, default='30')

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    @api.model
    def create(self, vals):
        rec = super(sale_order_line, self).create(vals)
        if (not rec.order_id.payment_term_id) or (rec.order_id.payment_term_id and 'Immediate' not in rec.order_id.payment_term_id.name):
            if rec.order_id and rec.order_id.partner_id.warning_type=='blocked':
                msg = 'Can not confirm the order because the customer does not have enough credit. \
                            You can transition your billing policy to direct debit to be able to bill."'
                raise Warning(_(msg))
                return False
            if rec.order_id and rec.order_id.partner_id.warning_type!='none':
                
                if rec.order_id and rec.order_id.partner_id.warning_type in ('date','all'):
                    
                    d = timedelta(days=rec.order_id.partner_id.credit_limit_days)
                    # if rec.partner_id.payment_earliest_due_date==False:
                    #     return True
                    # data = datetime.strptime(rec.order_id.partner_id.payment_earliest_due_date, '%Y-%m-%d')
                    # if data + d < datetime.now():
                    #     msg = 'Can not confirm the order because the customer does not have enough credit. \
                    #         You can transition your billing policy to direct debit to be able to bill."'
                    #     raise Warning(_(msg))
                    #     return False
                if rec.order_id and rec.order_id.partner_id.warning_type in ('value','all'):
                    domain = [('order_id.partner_id', '=', rec.order_id.partner_id.id),
                              ('invoice_status', '=', 'to invoice'),
                              ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
                    order_lines = rec.env['sale.order.line'].search(domain)
                    none_invoiced_amount = sum([x.price_subtotal for x in order_lines])
                    # We sum from all the invoices that are in draft the total amount
                    domain = [
                        ('partner_id', '=', rec.order_id.partner_id.id), ('state', '=', 'draft')]
                    draft_invoices = self.env['account.invoice'].search(domain)
                    draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

                    available_credit = rec.order_id.partner_id.credit_limit - \
                        rec.order_id.partner_id.credit - \
                        none_invoiced_amount - draft_invoices_amount
                    self.write({'available_credit': available_credit})
                    if rec.order_id.amount_total > available_credit:
                        msg = 'Can not confirm the order because the customer does not have enough credit. \
                            You can transition your billing policy to direct debit to be able to bill."'
                        raise Warning(_(msg))
                        return False
        return rec

    # def available_credit(self):
        


    @api.multi
    def write(self, vals):
        if (not self.order_id.payment_term_id) or (self.order_id.payment_term_id and 'Immediate' not in self.order_id.payment_term_id.name):
            if self.order_id and self.order_id.partner_id.warning_type=='blocked':
                msg = 'Can not confirm the order because the customer does not have enough credit. \
                            You can transition your billing policy to direct debit to be able to bill."'
                raise Warning(_(msg))
                return False
            if self.order_id and self.order_id.partner_id.warning_type!='none':
                if self.order_id and self.order_id.partner_id.warning_type in ('date','all'):
                    d = timedelta(days=self.order_id.partner_id.credit_limit_days)
                    # if self.partner_id.payment_earliest_due_date==False:
                    #     return True
                    # data = datetime.strptime(self.order_id.partner_id.payment_earliest_due_date, '%Y-%m-%d')
                    # if data + d < datetime.now():
                    #     msg = 'Can not confirm the order because the customer does not have enough credit. \
                    #         You can transition your billing policy to direct debit to be able to bill."'
                    #     raise Warning(_(msg))
                    #     return False
                if self.order_id and self.order_id.partner_id.warning_type in ('value','all'):
                    domain = [('order_id.partner_id', '=', self.order_id.partner_id.id),
                              ('invoice_status', '=', 'to invoice'),
                              ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
                    order_lines = self.env['sale.order.line'].search(domain)
                    none_invoiced_amount = sum([x.price_subtotal for x in order_lines])
                    # We sum from all the invoices that are in draft the total amount
                    domain = [
                        ('partner_id', '=', self.order_id.partner_id.id), ('state', '=', 'draft')]
                    draft_invoices = self.env['account.invoice'].search(domain)
                    draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

                    available_credit = self.order_id.partner_id.credit_limit - \
                        self.order_id.partner_id.credit - \
                        none_invoiced_amount - draft_invoices_amount
                    if self.order_id.amount_total > available_credit:
                        msg = 'Can not confirm the order because the customer does not have enough credit. \
                            You can transition your billing policy to direct debit to be able to bill."'
                        raise Warning(_(msg))
                        return False
        return super(sale_order_line, self).write(vals)


class sale_order(models.Model):
    _inherit = "sale.order"

    available_credit = fields.Float(
        string="Available Credit",
        compute='_available_credit'
    )

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('waiting', 'Waiting Approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')], 'Status')

    def _available_credit(self):
        domain = [
            ('partner_id', '=', self.partner_id.id)
        ]
        draft_invoices = self.search(domain)
        draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

        self.available_credit = self.partner_id.credit_limit - \
            draft_invoices_amount

    @api.multi
    def action_propose(self):
        context = dict(self._context)
        if self.available_credit > 0:
            self.write({
                'state': 'sale'
            })
        else:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'propose.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
                'nodestroy': True,
            }

    @api.one
    def action_wait(self):
        self.check_limit()
        return super(sale_order, self).action_wait()

    @api.one
    def action_confirm(self):
        self.check_limit()
        return super(sale_order, self).action_confirm()

    @api.one
    def check_limit(self):
        if self.payment_term_id and 'Immediate' not in self.payment_term_id.name:
            if self.partner_id.warning_type!='none':
                if self.partner_id.warning_type in ('date','all'):
                    d = timedelta(days=self.partner_id.credit_limit_days)
                    # if self.partner_id.payment_earliest_due_date==False:
                    #     return True
                    # data = self.partner_id.payment_earliest_due_date
                    # if data + d < datetime.now():
                    #     msg = 'Can not confirm the order because the customer does not have enough credit. \
                    #         You can transition your billing policy to direct debit to be able to bill."'
                    #     raise Warning(_(msg))
                    #     return False
                if self.order_id and self.order_id.partner_id.warning_type in ('value','all'):
                    # We sum from all the sale orders that are aproved, the sale order
                    # lines that are not yet invoiced
                    domain = [('order_id.partner_id', '=', self.partner_id.id),
                              ('invoice_status', '=', 'to invoice'),
                              ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
                    order_lines = self.env['sale.order.line'].search(domain)
                    none_invoiced_amount = sum([x.price_subtotal for x in order_lines])
                    # We sum from all the invoices that are in draft the total amount
                    domain = [
                        ('partner_id', '=', self.partner_id.id), ('state', '=', 'draft')]
                    draft_invoices = self.env['account.invoice'].search(domain)
                    draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

                    available_credit = self.partner_id.credit_limit - \
                        self.partner_id.credit - \
                        none_invoiced_amount - draft_invoices_amount
                    if self.amount_total > available_credit:
                        msg = 'Can not confirm the order because the customer does not have enough credit. \
                            You can transition your billing policy to direct debit to be able to bill."'
                        raise Warning(_(msg))
                        return False
        return True

            # self.write({'available_credit': available_credit})
