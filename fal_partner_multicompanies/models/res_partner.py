from odoo import fields, models, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    fal_child_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Children Companies',
        domain=[('is_company', '=', True)]
    )
    sale_order_count2 = fields.Integer(
        compute='_compute_sale_order_count2',
        string='# of Sales Order'
    )

    child_ids = fields.One2many(
        'res.partner', 'parent_id', string='Contacts',
        domain=[('active', '=', True), ('is_company', '=', False)]
    )

    @api.multi
    def _compute_sale_order_count2(self):
        for partner in self:
            childs = self.search([('id', 'child_of', partner.id)])
            childs_ids = childs.ids
            sales = self.env['sale.order'].search(
                [('partner_id', 'in', childs_ids)]
            )
            partner.sale_order_count2 = len(sales)

    @api.multi
    def button_related_sales(self):
        for partner in self:
            childs = self.search([('id', 'child_of', partner.id)])
            childs_ids = childs.ids
            return {
                'name': _('Quotations / Sale Orders'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'domain': [('partner_id', 'in', childs_ids)],
                'target': 'current',
            }
