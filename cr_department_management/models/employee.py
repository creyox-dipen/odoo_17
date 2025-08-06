# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from odoo.fields import Many2one
from datetime import date

class Employee(models.Model):
    _name = "employee.employee"
    _description = "Employee data"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string = 'Name')
    image = fields.Binary(string = 'Image')
    street = fields.Char(string = 'Street')
    city = fields.Char(string = 'City')
    zip = fields.Char(string = 'Zip')
    state_id = fields.Many2one('res.country.state', 'State_id')
    country_id = Many2one('res.country', 'Country_id')
    birthdate = fields.Date(string = 'BirthDate')
    age = fields.Float(string = "Age", compute = 'countAge')
    mobile = fields.Char(string = 'Mobile')
    email = fields.Char(string = 'Email')
    barcode = fields.Char(string = "Barcode")
    job_time = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time')])
    notes = fields.Html(string = 'Notes')
    remarks = fields.Text(string = 'Remarks')
    is_hod = fields.Boolean(string = 'Is HOD')
    active = fields.Boolean(string = 'Active')

    @api.onchange("mobile")
    def setBarcode(self):
        self.barcode = self.mobile

    @api.depends('birthdate')
    def countAge(self):
        currentYear = date.today().year
        for i in self:
            if i.birthdate:
                birthYear = i.birthdate.year
                i.age = currentYear - birthYear
            else:
                i.age = 0

    # @api.constrains('city')
    # def check_age_positive(self):
    #     if self.city  == 'rajkot':
    #         raise ValueError('city should not be rajkot')

    # @api.autovacuum
    # def remove_inactive_employees(self):
    #     """Remove inactive employee records."""
    #     self.env['employee.employee'].search([('active', '=', False)]).unlink()

    @api.model_create_multi
    def create(self):
        vals = [{'name' : 'test_emp_1', 'city' : 'ahmedabad', 'active' : 'True'}, {'name' : 'test_emp_2', 'city' : 'jamnagar', 'active' : 'True'}]
        records = super(Employee, self).create(vals)
        return records