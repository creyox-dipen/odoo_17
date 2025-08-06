# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
from datetime import date


class Student(models.Model):
    _name = "student.student"
    _inherit = ['mail.thread', 'mail.activity.mixin',]
    _description = "Log of data processing operations"
    _rec_name = 'city'

    sequence = 0

    seq = fields.Char(string='Sequence', readonly="True")
    name = fields.Char(string = 'Name')
    image = fields.Binary(string = 'Image')
    street = fields.Char(string = 'Street')
    city = fields.Char(string = 'City')
    state_id = fields.Many2one('res.country.state', 'State_id')
    country_id = fields.Many2one('res.country', 'Country_id')
    zip = fields.Char(string = 'Zip')
    birthdate = fields.Date(string = 'BirthDate')
    age = fields.Float(string = "Age", compute = 'countAge')
    mobile = fields.Char(string = 'Mobile', tracking=1)
    email = fields.Char(string = 'Email')
    barcode = fields.Char(string = "Barcode")
    department_id = fields.Many2one('department.department', 'Department_id',default= lambda self:self.env['department.department'].search([('name', '=', 'Electrical')]))
    types = fields.Selection([('external', 'External'), ('internal', 'Internal')])
    notes = fields.Html(string = 'Notes')
    remarks = fields.Text(string = 'Remarks')
    is_cr = fields.Boolean(string = 'Is_cr')
    cr_start_date = fields.Date(string = 'Cr_start_date')
    cr_end_date = fields.Date(string = 'Cr_end_date')
    no_of_votes = fields.Integer(string = 'no_of_votes')
    active = fields.Boolean(string = 'Active')
    dept_code = fields.Char(string='department code', related='department_id.code', store='True')

    @api.onchange("mobile")
    def setBarcode(self):
        self.barcode = self.mobile

    @api.depends('birthdate')
    def countAge(self):
        currentYear = date.today().year
        for i in self:
            if i.birthdate:
                birthYear = i.birthdate.year
                i.age = float(currentYear - birthYear)
            else :
                i.age = 0

    def create(self, vals_list,):
        # Student.sequence += 1
        # vals_list['seq'] = 'stud_' + str(Student.sequence).zfill(5) # custom logic
        vals_list['seq'] = self.env['ir.sequence'].next_by_code('student.student')
        createVar = super(Student, self).create(vals_list)
        return createVar