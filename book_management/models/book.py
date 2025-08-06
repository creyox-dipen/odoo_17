# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class Book(models.Model):
    _name = "book_model"
    _description = "This is Book model"

    title = fields.Char(String="Title : ")
    description = fields.Text(string="Description : ")
    price = fields.Float(String="Price : ")
    feedback = fields.Html(String="Feedback : ")
    publishdate = fields.Date(String="Publish Date : ")
    category = fields.Selection([('history', 'History'), ('science', 'Science'), ('physics', 'Physics')])
    image = fields.Image(String="Choose Image : ")

