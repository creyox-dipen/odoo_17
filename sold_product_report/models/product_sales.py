# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import models, fields, api, _


class ProductSaleReport(models.Model):
    _name = 'product.sale.report'
    _description = 'Product Sales Report'

    start_date = fields.Date(required=True, default=fields.Date.today().strftime('%Y-%m-%d 00:00:00'))
    end_date = fields.Date(required=True, default=fields.Date.today().strftime('%Y-%m-%d 23:59:59'))
    report_type = fields.Selection([('sale', 'Sale'), ('pos', 'Point of Sale'), ('both', 'Both')], default='sale', required=True)
    categ_id = fields.Many2many('product.category', string='Product Category')

    def product_sale_report(self):
        if self.report_type == 'sale':
            sale_orders = self.env['sale.order'].search(
                [('company_id', '=', self.env.company.id), ('date_order', '>=', self.start_date),
                 ('date_order', '<=', self.end_date), ('state', 'in', ['sale', 'done'])])
            products_sold = {}
            for order in sale_orders:
                for line in order.order_line:
                    if line.product_id.type != 'product':
                        continue
                    else:
                        if self.categ_id:
                            if line.product_id.categ_id in self.categ_id:
                                key = line.product_id
                                products_sold.setdefault(key, 0.0)
                                products_sold[key] += line.product_uom_qty
                        else:
                            key = line.product_id
                            products_sold.setdefault(key, 0.0)
                            products_sold[key] += line.product_uom_qty
            data = {
                'products': sorted([{
                    'product_id': product.id,
                    'product_name': product.name,
                    'barcode': product.barcode,
                    'quantity': qty,
                } for (product), qty in products_sold.items()], key=lambda l: l['product_name']),
                'type': ([{
                    'report_type': dict(self._fields['report_type'].selection).get(self.report_type),
                }])
            }
            return data

        elif self.report_type == 'pos':
            pos_orders = self.env['pos.order'].search(
                [('company_id', '=', self.env.company.id), ('date_order', '>=', self.start_date),
                 ('date_order', '<=', self.end_date), ('state', 'in', ['paid', 'invoiced', 'done'])])
            products_sold = {}
            for order in pos_orders:
                for line in order.lines:
                    if line.product_id.type != 'product':
                        continue
                    else:
                        if self.categ_id:
                            if line.product_id.categ_id in self.categ_id:
                                key = line.product_id
                                products_sold.setdefault(key, 0.0)
                                products_sold[key] += line.qty
                        else:
                            key = line.product_id
                            products_sold.setdefault(key, 0.0)
                            products_sold[key] += line.qty
            data = {
                'products': sorted([{
                    'product_id': product.id,
                    'product_name': product.name,
                    'barcode': product.barcode,
                    'quantity': qty,
                } for (product), qty in products_sold.items()], key=lambda l: l['product_name']),
                'type': ([{
                    'report_type': dict(self._fields['report_type'].selection).get(self.report_type),
                }])
            }
            return data

        else:
            sale_orders = self.env['sale.order'].search(
                [('company_id', '=', self.env.company.id), ('date_order', '>=', self.start_date),
                 ('date_order', '<=', self.end_date), ('state', 'in', ['sale', 'done'])])
            products_sold = {}
            for order in sale_orders:
                for line in order.order_line:
                    if line.product_id.type != 'product':
                        continue
                    else:
                        if self.categ_id:
                            if line.product_id.categ_id in self.categ_id:
                                key = line.product_id
                                products_sold.setdefault(key, 0.0)
                                products_sold[key] += line.product_uom_qty
                        else:
                            key = line.product_id
                            products_sold.setdefault(key, 0.0)
                            products_sold[key] += line.product_uom_qty

            pos_orders = self.env['pos.order'].search(
                [('company_id', '=', self.env.company.id), ('date_order', '>=', self.start_date),
                 ('date_order', '<=', self.end_date), ('state', 'in', ['paid', 'invoiced', 'done'])])
            for order in pos_orders:
                for line in order.lines:
                    if line.product_id.type != 'product':
                        continue
                    else:
                        if self.categ_id:
                            if line.product_id.categ_id in self.categ_id:
                                key = line.product_id
                                products_sold.setdefault(key, 0.0)
                                products_sold[key] += line.qty
                        else:
                            key = line.product_id
                            products_sold.setdefault(key, 0.0)
                            products_sold[key] += line.qty
            data = {
                'products': sorted([{
                    'product_id': product.id,
                    'product_name': product.name,
                    'barcode': product.barcode,
                    'quantity': qty,
                } for (product), qty in products_sold.items()], key=lambda l: l['product_name']),
                'type': ([{
                    'report_type': dict(self._fields['report_type'].selection).get(self.report_type),
                }])
            }
            return data

    def generate_product_sale_report(self):
        return self.env.ref('sold_product_report.report_product_sale').report_action([], )
