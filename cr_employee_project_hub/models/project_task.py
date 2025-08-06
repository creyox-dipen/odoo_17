# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from docutils.parsers.rst.directives import percentage

from odoo import models, fields, api
import random

class ProjectTask(models.Model):
    _inherit = ["project.task"]

    recommended_for = fields.Many2many(string="Assign Employee", comodel_name="hr.employee")
    skill_match_percent = fields.Char(string='Skill Percent', compute='count_skill_match_percentage', store='True')
    assigned_to_ids = fields.Many2many(string='Assigned To', comodel_name="res.partner")
    task_completed_employee = fields.Char(string='Task Completed Employee', related='recommended_for.name', domain=[('recommended_for.training_record_ids.status', '=', 'completed')])
    required_training = fields.Many2many(string='Required Training', comodel_name='training.session')

    def suggest_task_assignees(self):
        employee_recs = self.env['employee.training.record'].search([('status', '=', 'completed')])
        if len(list(employee_recs)) <= 5:
            return{
                'name': 'Task Assignees',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.training.record',
                'view_mode': 'tree',
                'domain': [('id', 'in', employee_recs.ids)]
            }
        else :
            random_employees = random.sample(employee_recs.ids, 5)
            return{
                'name': 'Task Assignees',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.training.record',
                'view_mode': 'tree',
                'domain': [('id', 'in', random_employees)]
            }

    @api.onchange('project_id')
    def reset_assignees_on_project_update(self):
        self.user_ids = None

    @api.depends('recommended_for')
    def count_skill_match_percentage(self):
        percent_format = f" "
        required_training_recs = self.required_training.ids  # list of required training ids
        if len(required_training_recs) :
            for employee in self.recommended_for:
                percentage = 0
                completed_training_recs = self.env['employee.training.record'].search([('employee_id', '=', employee.id), ('status', '=', 'completed')])
                training_rec_ids = []
                for rec in completed_training_recs:
                    training_rec_ids.append(rec.training_id.id)

                matched_skills = set(required_training_recs).intersection(set(training_rec_ids))
                percentage = (len(list(matched_skills)) * 100) / len(required_training_recs)
                percent_format += f"{employee.name} : {percentage}%, "
        self.skill_match_percent = percent_format