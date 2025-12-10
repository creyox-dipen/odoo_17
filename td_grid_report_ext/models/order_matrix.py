# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_report_matrixes(self):
        matrixes = super().get_report_matrixes()
        for matrix in matrixes:
            template_id = matrix.get('product_template_id')
            if not template_id:
                header_names = [h.get('name') for h in matrix.get('header', []) if h.get('name')]
                tmpl = self.order_line.mapped('product_template_id').filtered(
                    lambda t: t.display_name in header_names
                )[:1]
            else:
                tmpl = self.env['product.template'].browse(template_id)
            if tmpl:
                OrderCurrency = self.currency_id or self.order_id.currency_id
                lines = self.order_line.filtered(lambda l: l.product_template_id == tmpl)
                matrix['product_name'] = tmpl.name
                matrix['total_qty'] = round(sum(lines.mapped('product_uom_qty')), 2)
                matrix['total_subtotal'] = f"{OrderCurrency.symbol} {round(sum(lines.mapped('price_subtotal')), 2)}"
        return matrixes


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def verify_order(self):
        template = self.product_id.product_tmpl_id
        if len(self.order_id.order_line.filtered(lambda line: line.product_template_id == template)) > 1:
            return False
        else :
            return True