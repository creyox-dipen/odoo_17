from odoo import models, fields, api

class AbstractModel(models.AbstractModel):
    _name = "abstract.model"
    _description = 'My common model'

    name = fields.Char(string='Name')
    age = fields.Integer(string='Age')
    salary = fields.Float(string='Salary')
    country = fields.Many2one(comodel_name='res.country', string='Country')

