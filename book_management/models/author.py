# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api

class Author(models.Model):
    _name = "author_model"
    _description = "Author data"

    name = fields.Char(String = "Name : ")
    description = fields.Text(string= "Description : ")
    age = fields.Integer(String = "Age : ", compute='temporary_compute_method', store='True')
    salary = fields.Float(String = "Salary : ")
    feedback = fields.Html(String = "Feedback : ")
    birthdate = fields.Date(String = "Birth Date : ")
    isIndian = fields.Boolean(String = "Is Indian : ")
    image = fields.Image(String = "Choose Image : ")

    def crete_record(self):
        print(self)
        print(self.name, self.age)
        vals = {
            'name': 'mehul',
            'age': 21
        }
        print(self.env['author_model'].create(vals))

    @api.depends('salary')
    def temporary_compute_method(self):
        print("compute invoked")
        print(self)
        self.age = 50

    # def orm_operation(self):
    #     print(self)
    #     print(self[0])

    # def unlink(self):
    #     print("i am unlink method")
    #     print(self)
    #     returned_val = super(Author, self).unlink()
    #     print(returned_val)
    #     return

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # vals_list is a list of dictionaries, each for a new product
    #     vals_list = [{'name': 'dipen'},{'name': 'rajan'},{'name': 'jay'}]
    #     products = super(Author, self).create(vals_list)
    #     return products


