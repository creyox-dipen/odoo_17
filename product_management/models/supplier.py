# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class Supplier(models.Model):
    _name = 'supplier_model'
    _description = 'Supplier Model'

    name = fields.Char(string='Name')
    mobile = fields.Char(string='Mobile Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    notes = fields.Char(string='Notes')
    active = fields.Boolean(string='Active', default='True')
