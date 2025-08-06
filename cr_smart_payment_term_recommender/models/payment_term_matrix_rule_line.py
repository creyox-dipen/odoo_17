# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api

class PaymentTermMatrixRuleLine(models.Model):
    _name = "payment.term.matrix.rule.line"

    rule_id = fields.Many2one(comodel_name='payment.term.matrix.rule', string='Rules')
    operator = fields.Selection([('lt', '<'), ('le', '<='), ('eq', '='), ('gt', '>'), ('ge', '>='), ('between', 'Between')], required='True',string='Operator')
    value_1 = fields.Float(string='First Value', required='True')
    value_2 = fields.Float(string='Second Value', required='True')
    score = fields.Float(string='Score')
    active = fields.Boolean(string='Active', default='True')