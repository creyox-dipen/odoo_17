# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = ['product.template']
    _description = 'inherited the product.template model'

    average_rating = fields.Float(string='Average Rating', compute='count_average_rating', store='True')
    review_ids = fields.Html(string='Reviews', compute='format_reviews')

    @api.depends('review_ids')
    def count_average_rating(self):
        print(self)
        print("inside average Rating")
        for product_tmpl in self :
            product_record = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.id)])
            for product in product_record :
                reviews = self.env['product.review'].search([('product_id', '=', product.id), ('is_approved', '=', True)])
                print(reviews)
                if len(list(reviews)) > 0:
                    sum = 0
                    for review in reviews:
                        sum += int(review.rating)
                    average = sum / (len(list(reviews)))
                    product_tmpl.average_rating = average
                else :
                    product_tmpl.average_rating = 0

    def format_reviews(self):
        product_records = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        for product in product_records :
            review_ids = self.env['product.review'].search([('product_id', '=', product.id)])
            value = """"""
            for review in review_ids:
                if review:
                    value += f"""
                        <div>
                            <p> Reviewer: {review.customer_id.name}</p>
                            <p widget='rating'> Rating: {self.customize_rating_to_star(review.rating)}</p>
                            <p> Comment: {review.comment}</p>
                        </div>
                        <hr>
                    """
                else:
                    value = False
            self.review_ids = value

    def customize_rating_to_star(self, rating):
        return f"{'★' * int(rating)}{'☆' * (5 - int(rating))} ({rating}/5)"

    def get_report_details(self):
        return {
            'name': 'review_report',
            'type': 'ir.actions.act_window',
            'res_model': 'product.review.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'current_product_template_id': self.id,
                'product_name' : self.name
            }
        }
