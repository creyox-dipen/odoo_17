# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from Tools.scripts.mailerdaemon import emparse_list

from odoo import models, fields, api


class EmployeeAssign(models.TransientModel):
    _name = 'employee.assign.wiz'
    _description = 'this wizard assigns employees to task based on training'

    project_based_employee = None

    project_id = fields.Many2one(string='Project', comodel_name='project.task')
    training_id = fields.Many2many(string='Employees', comodel_name='employee.training.record', domain=[('id', 'in', project_based_employee)])
    def assign_employees_to_task(self):
        employees = self.env['hr.employee'].search([('id', 'in', self.training_id.employee_id.ids)])
        self.project_id.recommended_for = employees


    @api.onchange('project_id')
    def filter_employee_training_record(self):
        required_training = self.project_id.required_training
        emp_training_recs = []
        for rec in required_training:
            for i in rec.record_ids:
                emp_training_recs.append(i.id)

        employee_training_records = self.env['employee.training.record'].search([('id', 'in', emp_training_recs), ('status', '=', 'completed')])
        # EmployeeAssign.project_based_employee = employee_training_records
        self.training_id = employee_training_records
