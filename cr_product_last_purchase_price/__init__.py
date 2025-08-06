# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from . import models

def my_post_init_hook(env):
    purchase_ids = env['purchase.order'].search([])
    for purchase in purchase_ids:
        order_line_ids = purchase.order_line
        for order in order_line_ids:
            product_id = order.product_id.id
            unit_price = order.price_unit
            product = env['product.product'].search([('id', '=', product_id)])
            product.write({'last_purchase_price': unit_price})
