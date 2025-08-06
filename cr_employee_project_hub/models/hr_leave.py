# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api
from datetime import datetime

class HrLeave(models.Model):
    _inherit = ['hr.leave']

    @api.onchange('date_from')
    def set_employee_status(self):
        print('on change on time off')
        print(self.employee_id)
        employee_id = self.employee_id.id
        if self.date_from.date() == datetime.today().date() and self.date_to.date() == datetime.today().date():
            employee = self.env['hr.employee'].browse(employee_id)
            print(employee)
            employee.write({'status' : 'onleave'})