# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class Department_transient(models.TransientModel):
    _name = 'department.conf'
    _description = 'department.conf'

    type = fields.Selection([('create', 'Create'), ('write', 'Write')])
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    department_id = fields.Many2one('department.department', 'Department_Id')

    def processData(self):

        if self.type == 'process':
            newRecord = {
                'name' : self.name,
                'code' : self.code,
                'active' : 'True'
            }
            self.env['department.department'].create(newRecord)

        else :
            if self.name and self.code :
                self.department_id.name = self.name
                self.department_id.code = self.code
            elif self.name :
                self.department_id.name = self.name
            elif self.code:
                self.department_id.code = self.code