# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api

class PaymentTermMatrix(models.Model):
    _name = "payment.term.matrix"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    type = fields.Selection([('numeric', 'Numeric'), ('percent', 'Percent'), ('monetary', 'Monetary'), ('ratio', 'Ratio'), ('days', 'Days'), ('count', 'Count')], string='Type')
    active = fields.Boolean(string='Active', default='True')