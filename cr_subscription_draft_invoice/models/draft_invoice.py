# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields

class SaleSubscriptionPlan(models.Model):
    _inherit = "sale.subscription.plan"
    _description = "Add option to create draft invoice"

    is_draft = fields.Boolean(string='Draft Invoice')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _handle_automatic_invoices(self, invoice, auto_commit):
        """
        Skip automatic payment & payment_exception
        when subscription plan is configured for draft invoices.
        """
        self.ensure_one()
        if self.plan_id.is_draft:
            # Explicitly ensure subscription is NOT marked as failed
            self.with_context(mail_notrack=True).write({
                'payment_exception': False
            })
            # Just return the draft invoice, no payment logic
            return invoice

        return super()._handle_automatic_invoices(invoice, auto_commit)