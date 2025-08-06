# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    def generate_purchase_excel_report(self):
        fp = BytesIO()
        filename = "purchase_report.xlsx"
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet("purchase_report")
        bold = workbook.add_format({"bold": True})
        center_format = workbook.add_format({"align": "center", "valign": "vcenter", "bold": True, "font_size": "24"})
        date_style = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        worksheet.merge_range("G1:K1", 'Purchase Report', center_format)
        worksheet.merge_range("B3:E3", 'Purchase Details', bold)
        # worksheet.write('A5', 'Department:', bold)
        # worksheet.write('B5', self.name)
        # worksheet.write('J5', 'Department Code:', bold)
        # worksheet.write('K5', self.code)
        # worksheet.write('A7', 'Staff:', bold)
        # staff_names = ', '.join([staff.name for staff in self.staff_ids])
        # worksheet.merge_range('B7:D7', staff_names)
        # worksheet.write('J7', 'Total Students:', bold)
        # worksheet.write('K7', str(self.no_of_students or 0))
        row = 6
        # worksheet.merge_range("B10:E10", 'Student Details', bold)
        student_headers = ['Product', 'Purchase Price', 'Purchase Date']
        for col_num, header in enumerate(student_headers):
            worksheet.write(row + 1, col_num, header, bold)
        row += 2
        for purchase in self:
            purchase_price = 
            worksheet.write(row, 0, purchase.product_id.name or '')
            worksheet.write(row, 1, purchase. or '')
            worksheet.write(row, 2, student.age or 0)

        row += 1
        workbook.close()

        attachment_id = self.env["ir.attachment"].create({
            "name": filename,
            "type": "binary",
            "datas": base64.b64encode(fp.getvalue()),
            "res_model": self._name,
            "res_id": self.id,
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/%s/datas/%s" % ("ir.attachment", attachment_id.id, filename), "target": "self",
        }