# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
import xlsxwriter, base64
from io import BytesIO

class HrEmployee(models.Model):
    _inherit = ["hr.employee"]

    training_record_ids = fields.One2many(comodel_name="employee.training.record", inverse_name="employee_id", string="Training Records")
    certified_skills = fields.Char(string='Certified Skills', compute="count_completed_trainings", store='True')
    status = fields.Selection([('active', 'Active'), ('inactive', 'In Active'), ('onleave', 'On Leave')],string="String")

    @api.depends('training_record_ids.status')
    def count_completed_trainings(self):
        print("employee training record compute")
        print(self)
        employee_training_recs = self.training_record_ids
        completed_trainings = ""
        for rec in employee_training_recs:
            if rec.status == 'completed':
                completed_trainings += f"{rec.training_id.name} - "

        self.certified_skills = completed_trainings

    def show_training_history(self):
        return {
            'name': 'Training History',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.training.record',
            'view_mode': 'tree',
            'target': 'new',
            'domain': [('employee_id', '=', self.id)]
        }

    def toggle_status(self):
        if self.status == False:
            self.status = 'active'
        elif self.status == 'active':
            self.status = 'inactive'
            employee_id = self.id
            print(employee_id)
            if self.status == 'inactive':
                employee_training_recs = self.env['employee.training.record'].search([('employee_id', '=', employee_id)])
                for rec in employee_training_recs:
                    if rec.status == 'in_progress':
                        rec.write({'status': 'pause'})
                print("done")
        elif self.status == 'inactive':
            self.status = 'active'

    # Generating Excel Report
    def generate_excel_report(self):
        fp = BytesIO()
        filename = "employee_excel_report.xlsx"
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet("employee_report")
        bold = workbook.add_format({"bold": True})
        center_format = workbook.add_format({"align": "center", "valign": "vcenter", "bold": True, "font_size": "24"})
        date_style = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        worksheet.merge_range("G1:K1", 'Employee Report', center_format)
        worksheet.merge_range("B3:E3", 'Employee Details', bold)
        worksheet.write('A5', 'Department:', bold)
        worksheet.write('B5', self.department_id.name)
        worksheet.write('J5', 'Company :', bold)
        worksheet.write('K5', self.company_id.name)
        worksheet.write('A7', 'Phone No :', bold)
        worksheet.merge_range('B7:D7', self.work_phone)
        worksheet.write('J7', 'Email :', bold)
        worksheet.write('K7', self.work_email)
        row = 10
        worksheet.merge_range("B10:E10", 'employee Trainings', bold)
        student_headers = ["Sr No", "Employee", "Training", "Status", "Feedback", "Job Title"]
        for col_num, header in enumerate(student_headers):
            worksheet.write(row + 1, col_num, header, bold)
        row += 2
        count = 0
        for rec in self.training_record_ids:
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