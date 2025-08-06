# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
import xlsxwriter, base64
from io import BytesIO

class TrainingSession(models.Model):
    _name = 'training.session'
    _description = 'training session model'

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    trainer = fields.Char(string="Trainer")
    description = fields.Text(string="Description")
    record_ids = fields.One2many(string="Employees", comodel_name="employee.training.record", inverse_name="training_id")

    def show_all_participants(self):
        emps = []
        for rec in self.record_ids:
            emps.append(rec.employee_id.id)
        return {
            'name': 'Employees',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree',
            'target': 'new',
            'domain': [('id', 'in', emps)]
        }

    # Generating Excel Report
    def generate_excel_report(self):
        fp = BytesIO()
        filename = "training_session_report.xlsx"
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet("training_session")
        bold = workbook.add_format({"bold": True})
        center_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "font_size": "24"})
        date_style = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        worksheet.merge_range("G1:K1", 'Training Report', center_format)
        worksheet.merge_range("B3:E3", 'Training Details', bold)
        worksheet.write('A5', 'Name :', bold)
        worksheet.write('B5', self.name)
        worksheet.write('J5', 'Date :', bold)
        worksheet.write('K5', str(self.date))
        worksheet.write('A7', 'Trainer :', bold)
        worksheet.merge_range('B7:D7', self.trainer)
        worksheet.write('J7', 'Description :', bold)
        worksheet.write('K7', self.description)
        row = 10
        worksheet.merge_range("B10:E10", 'employee Trainings', bold)
        student_headers = ["Sr No", "Employee", "Training", "Status", "Feedback", "Job Title"]
        for col_num, header in enumerate(student_headers):
            worksheet.write(row + 1, col_num, header, bold)
        row += 2
        count = 0
        for rec in self.record_ids:
            count += 1
            worksheet.write(row, 0, count or '')
            worksheet.write(row, 1, rec.employee_id.name or '')
            worksheet.write(row, 2, rec.training_id.name or 0)
            worksheet.write(row, 3, rec.status or '')
            worksheet.write(row, 4, rec.feedback or '', date_style)
            worksheet.write(row, 5, rec.employee_job_title or '')
            row += 1
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