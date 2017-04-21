from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    fal_child_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Children Companies',
        domain=[('is_company', '=', True)]
    )

    sale_order_count2 = fields.Integer(compute='_compute_sale_order_count2', string='# of Sales Order')

    def _compute_sale_order_count2(self):
        sale_data = self.env['sale.order'].read_group(domain=[('partner_id', 'child_of', self.ids)],
                                                      fields=['partner_id'], groupby=['partner_id'])
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in sale_data])
        for partner in self:
            partner_ids = filter(lambda r: r['id'] == partner.id, partner_child_ids)[0]
            partner_ids = [partner_ids.get('id')] + partner_ids.get('child_ids')
            partner.sale_order_count2 = sum(mapped_data.get(child, 0) for child in partner_ids)