# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from io import BytesIO
import xlsxwriter, base64
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = ['product.product']

    last_purchase_price = fields.Float(string='Last Purchase Price')
    last_purchase_date = fields.Date(string='Purchase Date')

    def generate_product_excel_report(self):
        fp = BytesIO()
        filename = "product_report.xlsx"
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet("product_report")
        bold = workbook.add_format({"bold": True, "valign": "vcenter", "font_size": "15"})
        center_format = workbook.add_format({"align": "center", "valign": "vcenter", "bold": True, "font_size": "24"})
        headers = workbook.add_format({"valign": "vcenter", "bold": True, "font_size": "13"})
        worksheet.merge_range("B1:D1", 'Product Details', bold)
        worksheet.merge_range("A3:D3", 'Product', headers)
        worksheet.merge_range("E3:F3", 'Purchase Price', headers)
        worksheet.merge_range("G3:H3", 'Purchase Date', headers)
        data_format = workbook.add_format({"valign": "vcenter", "align": "left"})
        rec_row = 4
        for product in self:
            worksheet.merge_range(f"A{rec_row}:D{rec_row}", product.name or '', data_format)
            worksheet.merge_range(f"E{rec_row}:F{rec_row}", product.last_purchase_price or '', data_format)
            worksheet.merge_range(f"G{rec_row}:H{rec_row}", str(product.last_purchase_date), data_format)
            rec_row += 1
        workbook.close()
        attachment_id = self.env["ir.attachment"].create({
            "name": filename,
            "type": "binary",
            "datas": base64.b64encode(fp.getvalue()),
            "res_model": self._name,
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/%s/datas/%s" % ("ir.attachment", attachment_id.id, filename), "target": "self",
        }

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        order_line_ids = self.order_line
        for order in order_line_ids:
            product_id = order.product_id.id
            unit_price = order.price_unit
            product = self.env['product.product'].search([('id', '=', product_id)])
            product.write({'last_purchase_price': unit_price, 'last_purchase_date': self.date_approve})
        return res

