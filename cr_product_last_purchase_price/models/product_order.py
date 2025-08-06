# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    # last_price = fields.Float(string='Last Price', compute='count_last_purchase_price')
    #
    # def count_last_purchase_price(self):
    #     print(self)
    #     self.last_price = 0