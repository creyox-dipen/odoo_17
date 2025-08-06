# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api


class TrainingSession(models.Model):
    _name = 'employee.training.record'
    _description = 'employee training record model'

    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    training_id = fields.Many2one(string="Training", comodel_name="training.session")
    status = fields.Selection([('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('pause', 'Pause')], string="Status", default='not_started')
    feedback = fields.Text(string="Feedback")
    employee_job_title = fields.Char(string='Job Title', related='employee_id.job_title')
    employee_name = fields.Char(string="Employee Name", related="employee_id.name")
    training_trainer = fields.Char(string="Training Trainer", related='training_id.trainer')
    training_date = fields.Date(string="Training Date", related='training_id.date')

    def start_employee_training(self):
        if self.status == 'not_started':
            self.status = 'in_progress'