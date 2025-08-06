# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from itertools import count

from odoo import models, fields, api
from odoo.odoo.odoo.tools.populate import compute


class Category(models.Model):
    _name = 'category_model'
    _description = 'Category Model'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    product_ids = fields.One2many('product_model', 'category_id')
    active = fields.Boolean(string='Active', default='True')
    total_items = fields.Integer(string='Total Items', compute='count_total_items')

    @api.depends('product_ids')
    def count_total_items(self):
        for category in self:
            category.total_items = len(list(category.product_ids))
