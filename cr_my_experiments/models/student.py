# Example of _inherits
from odoo import fields, models

class SaleOrderLine(models.Model):
    _name = "student.model"
    _description = "student model"
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(comodel_name='res.partner', )
    enno = fields.Char(string='Enrolment Number')

    def general_method(self):
        teacher_recs = self.env['teacher.model'].with_context({'check_access_rights': False}).search([])
        print(teacher_recs)