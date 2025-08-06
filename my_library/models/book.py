from odoo import models, fields

class Book(models.Model):
    _name = 'library.book'                  # Internal DB model name
    _description = 'Library Book'          # Human-readable name

    name = fields.Char(string="Title", required=True)        # Title of book
    author = fields.Char(string="Author")                    # Author name
    date_published = fields.Date(string="Published On")      # Date of publication

