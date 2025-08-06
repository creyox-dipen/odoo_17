# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo.exceptions import ValidationError, UserError, AccessDenied
from odoo import models, fields, api
import xlsxwriter, base64
from io import BytesIO

class Department(models.Model):
    _name = "department.department"
    _description = 'department model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'code'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    no_of_students = fields.Integer(string = "Total Students", compute='count_no_of_students', store='True')
    staff_ids = fields.Many2many('employee.employee', 'Staff_id')
    hod_id = fields.Many2one('employee.employee', 'hod_id', domain=[('is_hod', '=', 'True')])
    student_ids = fields.One2many('student.student', 'department_id', domain=[('types', '=', 'internal')])
    notes = fields.Html(string='Notes')
    active = fields.Boolean(string='Active', default='True')

    @api.depends('student_ids')
    def count_no_of_students(self):
        for i in self:
            sum = 0
            for stud in i.student_ids:
                sum += 1
            i.no_of_students = sum

    def insertRecord(self):
        print(self.student_ids)
        values = {
            'name': 'dipen',
            'code': '123',
            'notes': 'test note',
            'active': 'True'
        }
        self.env['department.department'].create(values)
        print(self)

    # it display the student tree view specific to department
    def showTotalStudents(self):
        dep_id = self.id
        return {
            'name' : 'Students',
            'type': 'ir.actions.act_window',
            'res_model' : 'student.student',
            'view_mode' : 'tree',
            'target' : 'new',
                'domain': [('department_id', '=', dep_id)]
        }

    # url action from python
    def goToYt(self):
        return {
            'type': 'ir.actions.act_url',
            'url': "https://www.youtube.com"
        }

    def testData(self):
        # print(self.env['department.department'].search([]))
        # sum = 0
        # for i in self.env['department.department'].search([]):
        #     sum += 1
        # print(sum)
        # self.no_of_students = sum

        print(self)
        print(self.browse(self.ids[0]))

    @api.onchange("code")
    def fetchData(self):
        print(self.staff_ids)

    def testFilter(self):
        all_records = self.env['department.department'].search([])
        print(all_records)
        filtered_data = all_records.filtered(lambda x: x.no_of_students > 1)
        print(filtered_data)

    def testMap(self):
        all_records = self.env['department.department'].search([])
        print(all_records)
        mappedRecords = all_records.mapped(lambda x : x.active==False)
        print(mappedRecords)

    def testUnlink(self):
        self.unlink()
        print("record deleted")

    def showException(self):
        raise AccessDenied("AccessDenied occured!!")

    def testPrints(self):
        dep_vals = self.env['department.department'].search([('name','=','computer')])
        print(dep_vals)
        stud_vals = self.env['student.student'].search([('city', '=', 'rajkot')])
        print(stud_vals)
        emp_vals = self.env['employee.employee'].search([('age', '>', '20')])
        print(emp_vals)

    # action server method
    def testActionMethod(self):
        print("i am from action server method")
        print(self)
        for rec in self:
            print(rec.name)

    def removeInactive(self):
        print(self.env['department.department'].search([]))
        print("i am from xml schedule action")
        # code to remove inactive data

    # creating Schedule action from python side with orm(create) method
    def makeScheduleAction(self):
        crons = self.env['ir.cron'].create([
            {
                'active': False,
                'interval_type': 'minutes',
                'interval_number': 1,
                'numbercall': -1, # -1 means infinite times
                'doall': False,
                'name': "python ir cron",
                'model_id': self.env['ir.model']._get_id(self._name), # returns the id of the model
                'state': 'code',
                'code': "model.testScheduleAction()",
            }
        ])

    # to send notification
    def showNotification(self):
        self.env['bus.bus']._sendone(self.env.user.partner_id,'simple_notification', {
            'type' : 'success',
            'title' : 'Notification!!',
            'message' : 'This is Success Notification',
            'sticky' : True
        })

    def testScheduleAction(self):
        print("i am from python schedule action")
        print("this is will print after every minute")


    # it displays custom name in relational field (after 16 _compute_display_name method is used instead of name_get)
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.code}] {record.name}"

    # sending mail using template that is crafted in xml file
    def sendMail(self):
        # give the template id like module_name.template_id in self.env.ref
        mail_template = self.env.ref('cr_department_management.department_email_template_id')
        context = {
            'name' : 'dipen',
            'topic' : 'Email Topic',
        }
        mail_template.send_mail(self.id, email_values=context)
        print(mail_template)

    # sending mail only from python side
    def send_mail(self):
        body_html = (
            '<p> Dear Customer, </p>'
            '<p>Your order status has been updated | <strong>UPDATED</strong> </p>'
            '<p>Thank you for shopping with us 😊'
        )
        mail_values = {
            'subject' : 'Order Status Change Notification',
            'body_html': body_html,
            'email_to': 'dipen.dev@gmail.com',
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    def generate_excel_report(self):
        fp = BytesIO()
        filename = "my_department_report.xlsx"
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet("Department_report")
        bold = workbook.add_format({"bold": True})
        center_format = workbook.add_format({"align": "center", "valign": "vcenter", "bold": True, "font_size": "24"})
        date_style = workbook.add_format({'num_format': 'dd-mm-yyyy'})
        worksheet.merge_range("G1:K1", 'Department Report', center_format)
        worksheet.merge_range("B3:E3", 'Department Details', bold)
        worksheet.write('A5', 'Department:', bold)
        worksheet.write('B5', self.name)
        worksheet.write('J5', 'Department Code:', bold)
        worksheet.write('K5', self.code)
        worksheet.write('A7', 'Staff:', bold)
        staff_names = ', '.join([staff.name for staff in self.staff_ids])
        worksheet.merge_range('B7:D7', staff_names)
        worksheet.write('J7', 'Total Students:', bold)
        worksheet.write('K7', str(self.no_of_students or 0))
        row = 10
        worksheet.merge_range("B10:E10", 'Student Details', bold)
        student_headers = ["Sr No", "Name", "Age", "Email", "Birthdate", "Phone"]
        for col_num, header in enumerate(student_headers):
            worksheet.write(row + 1, col_num, header, bold)
        row += 2
        for student in self.student_ids:
            worksheet.write(row, 0, student.id or '')
            worksheet.write(row, 1, student.name or '')
            worksheet.write(row, 2, student.age or 0)
            worksheet.write(row, 3, student.email or '')
            worksheet.write(row, 4, student.birthdate or '', date_style)
            worksheet.write(row, 5, student.mobile or '')
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