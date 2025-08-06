from odoo import models, fields, api

class TeacherModel(models.Model):
    _name = "teacher.model"
    _inherit = ['abstract.model']

    is_hod = fields.Boolean(string='Is HOD')
    gender = fields.Selection([('male', 'Male'),('female', 'Female')])