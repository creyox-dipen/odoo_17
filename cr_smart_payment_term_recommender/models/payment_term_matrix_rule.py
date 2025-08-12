# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PaymentTermMatrixRule(models.Model):
    _name = "payment.term.matrix.rule"

    matrix_id = fields.Many2one(
        comodel_name="payment.term.matrix", string="Matrix", required=True
    )
    rule_line_ids = fields.One2many(
        comodel_name="payment.term.matrix.rule.line",
        inverse_name="rule_id",
        required=True,
    )

    @api.onchange("matrix_id")
    def _onchange_category_id(self):
        if len(list(self.matrix_id)):
            defined_matrix_recs = self.env["payment.term.matrix.rule"].search([])
            defined_matrix_ids = []
            for rec in defined_matrix_recs:
                defined_matrix_ids.append(rec.matrix_id.id)
            if self.matrix_id.id in defined_matrix_ids:
                raise ValidationError(
                    "The rules for this KPI have already been defined !!"
                )
