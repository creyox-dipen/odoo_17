# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class JournalConfiguration(models.Model):
    _name = "journal.configuration"
    _description = "Model for Journal Configuration"

    cb_config_id = fields.Many2one(comodel_name="chargebee.configuration")
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        # domain=lambda self: [("id", "not in", self._get_used_company_ids())],
    )
    invoice_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="[('company_id', '=', company_id), ('type', '=', 'sale')]",
        required=True,
    )
    invoice_payment_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
        required=True,
    )
    credit_note_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="[('company_id', '=', company_id), ('type', '=', 'sale')]",
        required=True,
    )
    credit_note_payment_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
        required=True,
    )
    item_family_id = fields.Many2one(
        comodel_name="chargebee.item.family",
        required=True,
    )

    # @api.model
    # def _get_used_company_ids(self):
    #     used = self.search([]).mapped("company_id").ids
    #     return used

    # @api.constrains("company_id")
    # def _check_unique_company(self):
    #     for rec in self:
    #         exists = self.search(
    #             [("company_id", "=", rec.company_id.id), ("id", "!=", rec.id)]
    #         )
    #         if exists:
    #             raise ValidationError(
    #                 "A configuration already exists for this company."
    #             )
