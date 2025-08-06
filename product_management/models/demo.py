from io import BytesIO

import xlsxwriter, base64
def action_generate_excel_report(self):
    fp = BytesIO()
    file_name = "department_report.xlsx"
    workbook = xlsxwriter.Workbook(fp, {"in_memory": True})
    worksheet = workbook.add_worksheet("Department Report")
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
        "name": file_name,
        "type": "binary",
        "datas": base64.b64encode(fp.getvalue()),
        "res_model": self._name,
        "res_id": self.id,
    })
    return {
        "type": "ir.actions.act_url",
        "url": "/web/content/%s/%s/datas/%s" % ("ir.attachment", attachment_id.id, file_name), "target": "self",
    }