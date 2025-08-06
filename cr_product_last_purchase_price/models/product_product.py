# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = ['product.product']

    last_purchase_price = fields.Float(string='Last Purchase Price')

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()

        order_line_ids = self.order_line
        for order in order_line_ids:
            product_id = order.product_id.id
            unit_price = order.price_unit
            product = self.env['product.product'].search([('id', '=', product_id)])
            product.write({'last_purchase_price': unit_price})

        return res