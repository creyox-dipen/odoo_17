# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class ChargebeeTaxConfiguration(models.Model):
    _name = "chargebee.tax.configuration"
    _description = "Chargebee Tax Configuration"

    cb_config_id = fields.Many2one(
        comodel_name="chargebee.configuration",
        string="Chargebee Configuration",
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
    )
    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Customer Tax",
        domain="[('company_id', '=', company_id), ('type_tax_use', '=', 'sale')]",
        required=True,
    )
