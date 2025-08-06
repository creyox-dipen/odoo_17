# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class SplitSales(models.TransientModel):
    _name = 'split.sale.wiz'
    _description = 'split wizard'

    partner_id = fields.Many2one('res.partner', 'Partner Id')

    def splitProcess(self):
        sale_order_model = self.env['sale.order']
        sale_rec_id = self._context['sale_rec_id']
        sale_record = sale_order_model.browse(sale_rec_id)
        print(sale_record)
        print(sale_record.order_line)
        split_records = sale_record.order_line.filtered(lambda rec: rec.split == True)
        print(split_records)
        print(self.partner_id)

        newRecrod = {
            'partner_id' : self.partner_id.id,
            'order_line' : split_records.ids
        }
        sale_order_model.create(newRecrod)
