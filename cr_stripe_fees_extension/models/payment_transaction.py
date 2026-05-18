# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from odoo.addons.payment import utils as payment_utils
import logging

logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    fees = fields.Float(string="Fees")

    def _stripe_prepare_payment_intent_payload(self):
        res = super()._stripe_prepare_payment_intent_payload()
        stripe_provider = self.env["payment.provider"].search(
            [("code", "=", "stripe")], limit=1
        )

        if stripe_provider.is_extra_fees:
            base_amount = payment_utils.to_major_currency_units(
                res["amount"], self.currency_id
            )
            total_invoice_amount = base_amount
            total_fixed_fees = 0
            total_percent_fees = 0
            company_country = self.company_id.country_id

            if self.invoice_ids:
                invoice = self.invoice_ids[0]
                total_invoice_amount = invoice.amount_total
                partner_country = invoice.partner_id.country_id
            else:
                partner_country = self.partner_id.country_id

            logger.info("partner country : %s", partner_country.name)

            is_international = (
                partner_country
                and company_country
                and partner_country.id != company_country.id
            )

            if is_international:
                if not stripe_provider.is_free_international:
                    total_fixed_fees = (
                        base_amount * stripe_provider.fix_international_fees
                    ) / total_invoice_amount
                    total_percent_fees = (
                        stripe_provider.var_international_fees * base_amount
                    ) / 100

                else:
                    if (
                        not total_invoice_amount
                        >= stripe_provider.free_international_amount
                    ):
                        total_fixed_fees = (
                            base_amount * stripe_provider.fix_international_fees
                        ) / total_invoice_amount
                        total_percent_fees = (
                            stripe_provider.var_international_fees * base_amount
                        ) / 100

                self.fees = total_fixed_fees + total_percent_fees
                fees_minor_currency = payment_utils.to_minor_currency_units(
                    self.fees, self.currency_id
                )
                res["amount"] += fees_minor_currency

            else:
                if not stripe_provider.is_free_domestic:
                    total_fixed_fees = (
                        base_amount * stripe_provider.fix_domestic_fees
                    ) / total_invoice_amount
                    total_percent_fees = (
                        stripe_provider.var_domestic_fees * base_amount
                    ) / 100

                else:
                    if not total_invoice_amount >= stripe_provider.free_domestic_amount:
                        total_fixed_fees = (
                            base_amount * stripe_provider.fix_domestic_fees
                        ) / total_invoice_amount
                        total_percent_fees = (
                            stripe_provider.var_domestic_fees * base_amount
                        ) / 100

                self.fees = total_fixed_fees + total_percent_fees
                fees_minor_currency = payment_utils.to_minor_currency_units(
                    self.fees, self.currency_id
                )
                res["amount"] += fees_minor_currency

        return res
