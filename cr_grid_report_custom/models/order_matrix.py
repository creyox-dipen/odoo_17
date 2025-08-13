# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_report_matrixes(self):
        # Call the original method
        matrixes = super().get_report_matrixes()
        for matrix in matrixes:
            template_id = matrix.get('product_template_id')

            if not template_id:
                # Try to deduce from matrix data (first variant line usually has it)
                header_names = [h.get('name') for h in matrix.get('header', []) if h.get('name')]
                # Match template based on name in order lines
                tmpl = self.order_line.mapped('product_template_id').filtered(
                    lambda t: t.name in header_names
                )[:1]
            else:
                tmpl = self.env['product.template'].browse(template_id)

            if tmpl:
                # Filter only lines of this product template
                lines = self.order_line.filtered(lambda l: l.product_template_id == tmpl)

                matrix['product_name'] = tmpl.name
                matrix['total_qty'] = sum(lines.mapped('product_uom_qty'))
                matrix['total_subtotal'] = sum(lines.mapped('price_subtotal'))

        return matrixes



