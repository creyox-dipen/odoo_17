# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = ['product.product']

    no_of_reviews = fields.Integer(string='Total Reviews', compute='count_no_of_reviews')
    review_ids = fields.One2many(comodel_name='product.review', inverse_name='product_id', string='Reviews')

    def show_related_reviews(self):
        print(self)
        product_id = self.id
        return {
            'name': 'Reviews',
            'type': 'ir.actions.act_window',
            'res_model': 'product.review',
            'view_mode': 'tree',
            'target': 'new',
            'domain': [('product_id', '=', product_id)]
        }

    @api.depends('review_ids.comment')
    def count_no_of_reviews(self):
        print("i am inside")
        self.no_of_reviews = 0