# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
from datetime import datetime, timedelta

class ProductReview(models.Model):
    _name = "product.review"
    _description = "Product Review Model"

    product_id = fields.Many2one('product.product', string='Product')
    customer_id = fields.Many2one('res.partner', string='Customer')
    rating = fields.Selection([('0',0),('1',1),('2',2),('3',3),('4',4),('5',5)], string='Rating')
    review_date = fields.Date(string='Review Date')
    comment = fields.Text(string='Comment')
    is_approved = fields.Boolean(string='Is Approved')
    product_name = fields.Char(string='Product Name', related='product_id.name')
    # product_price = fields.Monetary(string='Product Price', related='product_id.base_unit_price')
    product_category = fields.Char(string='Product Category', related='product_id.categ_id.name')
    active = fields.Boolean(string='Active', default = True)
    status = fields.Selection([('unapproved', 'Unapproved'), ('approved', 'Approved')], compute="manage_review_status", readonly="True", string="Status", default='unapproved')

    # @api.constrains('rating')
    # def check_rating_under_5(self):
    #     if not int(self.rating) >= 0 and int(self.rating) <= 5:
    #         raise ValueError('Rating should be 1-5 !!')

    def inactive_older_review(self):
        reviews = self.search([])
        six_months_ago = datetime.today().date() - timedelta(days= 180)
        for review in reviews:
            if review.review_date < six_months_ago:
                review.active = False

    @api.depends('is_approved', 'rating')
    def manage_review_status(self):
        for rec in self:
            if rec.is_approved == False:
                rec.status = 'unapproved'
            else :
                rec.status = 'approved'

    def admin_approve_review(self):
        self.is_approved = True
        self.status = 'approved'

    def admin_reject_review(self):
        self.is_approved = False
        self.status = 'unapproved'