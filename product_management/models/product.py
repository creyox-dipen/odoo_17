# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class Product(models.Model):
    _name = 'product_model'
    _description = 'Product Model'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    total_amount = fields.Float(string="Total Amount", compute='count_total_amount', readonly="True")
    quantity = fields.Float(string='Quantity')
    total_stock = fields.Integer(string='Total Stock', readonly="True")
    category_id = fields.Many2one('category_model', string='Category')
    image = fields.Binary(string='Image')
    supplier_id = fields.Many2one('supplier_model', string="Supplier")
    active = fields.Boolean(string='Active', default='True')
    supplier_contact = fields.Char(string='Supplier Contact', related='supplier_id.mobile' )

    @api.onchange('quantity')
    def setTotalStock(self):
        self.total_stock = self.quantity

    @api.depends('price', 'quantity')
    def count_total_amount(self):
        for product in self:
            product.total_amount = product.price * product.quantity

    def show_supplier_details(self):
        supplier_id = self.supplier_id.id
        print(self.supplier_id)
        return {
            'name': 'Supplier',
            'type': 'ir.actions.act_window',
            'res_model': 'supplier_model',
            'view_mode': 'tree',
            'target': 'new',
            'domain': [('id', '=', supplier_id)]
        }