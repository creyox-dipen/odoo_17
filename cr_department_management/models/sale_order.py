# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = ['sale.order.line']

    split = fields.Boolean(string='split')

class sale_order(models.Model):
    _inherit = ['sale.order']

    def split(self):
        return {
            'name' : 'Split',
            'type' : 'ir.actions.act_window',
            'res_model' : 'split.sale.wiz',
            'view_mode' : 'form',
            'target' : 'new',
            'context' : { # by context we can pass extra information
              'sale_rec_id' : self.id
            },
        }