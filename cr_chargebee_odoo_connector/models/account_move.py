# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import chargebee
from datetime import datetime, timezone
import logging
import json
import pytz
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    chargebee_id = fields.Char(
        string="Chargebee Invoice ID", help="ID of the invoice in Chargebee"
    )
    chargebee_invoice_url = fields.Char(
        string="Chargebee Invoice URL", help="Link to the invoice in Chargebee"
    )
    linked_payments = fields.Text(
        string="Linked Payments", help="Details of linked payments stored as JSON"
    )
    adjustments = fields.Text(
        string="Adjustments", help="Adjustment credit notes stored as JSON"
    )

    def convert_timestamp_to_datetime(self, timestamp):
        """Convert a timestamp to a datetime object."""
        if timestamp:
            return fields.Datetime.to_string(datetime.utcfromtimestamp(timestamp))
        return None

    def convert_timestamp_to_date_for_deffered(self, timestamp):
        """Convert Unix timestamp to date without timezone shift issues."""
        if not timestamp:
            return None

        # Convert timestamp to datetime in UTC
        dt_utc = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)

        # Add 12 hours to avoid timezone boundary issues, then extract date
        # This ensures we get the correct date regardless of timezone
        dt_adjusted = dt_utc + relativedelta(hours=12)

        return fields.Date.to_string(dt_adjusted.date())

    def convert_timestamp_to_utc(timestamp):
        """Convert Unix timestamp to UTC datetime."""
        if timestamp:
            try:
                return datetime.utcfromtimestamp(timestamp)
            except (ValueError, OSError):
                _logger.error(f"Invalid timestamp: {timestamp}")
                return None
        return None

    def _is_reconciled(self):
        """Check if a journal entry is fully reconciled."""
        return all(line.reconciled for line in self.line_ids)

    def fetch_total_cycles_of_the_subscription(self, quote):
        """Calculate total cycles of the subscription (past + current + remaining)"""

        ramp_item = quote.quoted_ramp.line_items[0]
        start = datetime.fromtimestamp(ramp_item.start_date)
        end = datetime.fromtimestamp(ramp_item.end_date)
        billing_period = ramp_item.billing_period or 1
        billing_period_unit = ramp_item.billing_period_unit
        delta = relativedelta(end, start)
        if billing_period_unit == "month":
            total_months = delta.years * 12 + delta.months
            return total_months // billing_period

        if billing_period_unit == "year":
            total_years = delta.years
            return total_years // billing_period

        if billing_period_unit == "week":
            total_days = (end - start).days
            return total_days // (billing_period * 7)

        if billing_period_unit == "day":
            total_days = (end - start).days
            return total_days // billing_period

        raise ValueError(f"Unsupported billing_period_unit: {billing_period_unit}")

    @api.model_create_multi
    def create(self, vals_list):
        # skip if module not completely installed
        if not self.env.registry.ready:
            return super().create(vals_list)

        _logger.info("➡️➡️ create method invoked.")
        invoices = super(AccountMove, self).create(vals_list)
        subscription_invoices = invoices.filtered(
            lambda m: m.ref and 'Subscription' in m.ref
        )

        if subscription_invoices:
            _logger.info(
                "Skipping post-create logic for subscription invoices: %s",
                subscription_invoices.ids,
            )
            return invoices

        chargebee_config = self.env["chargebee.configuration"].search([], limit=1)

        if (
                not chargebee_config
                or not chargebee_config.api_key
                or not chargebee_config.site_name
        ):
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        for invoice in invoices:
            if invoice.move_type == "out_refund":
                continue

            if invoice.move_type == "out_invoice":
                continue

            if invoice.chargebee_id:
                try:
                    # Skip reconciled invoices
                    if invoice._is_reconciled():
                        _logger.info(
                            f"Skipping reconciled invoice: {invoice.chargebee_id}"
                        )
                        continue
                    _logger.info("➡️➡️ invoice isn't reconciled.")
                    # Sync credit notes
                    self.sync_credit_notes(invoice)
                    _logger.info("➡️➡️ credit note function complete from create")
                    # Fetch payment details from Chargebee

                    payments = chargebee.Transaction.list(
                        {"invoice_id": invoice.chargebee_id}
                    )
                    _logger.info("➡️➡️ fetched transaction from create")
                    total_paid = 0

                    for payment_data in payments:
                        payment = payment_data.transaction
                        payment_date = self.convert_timestamp_to_datetime(payment.date)
                        payment_amount = (
                                payment.amount / 100
                        )  # Convert cents to currency
                        _logger.info("payment data : %s", payment_data)

                        # Get product IDs from invoice lines
                        product_ids = invoice.invoice_line_ids.mapped('product_id').ids
                        invoice_payment_journal = self._get_payment_journal(
                            chargebee_config,
                            invoice.company_id,
                            product_ids
                        )

                        # Create payment in Odoo
                        payment_vals = {
                            "partner_id": invoice.partner_id.id,
                            "amount": payment_amount,
                            "payment_date": payment_date,
                            "payment_type": "inbound",
                            "journal_id": invoice_payment_journal.id,
                            # "payment_method_line_id": self.env.ref(
                            #     "account.account_payment_method_manual_in"
                            # ).id,
                            "communication": f"Chargebee Payment: {payment.id}",
                        }
                        _logger.info("➡️➡️ creating payment from create method...")
                        _logger.info("➡️➡️ invoice state : %s", invoice.state)

                        if invoice.state != "posted":
                            invoice.action_post()
                        odoo_payment = (
                            self.env["account.payment.register"]
                            .with_context(
                                active_model="account.move", active_ids=[invoice.id]
                            )
                            .sudo()
                            .create(payment_vals)
                        )
                        _logger.info("⚒️⚒️ payment : %s", odoo_payment)
                        odoo_payment.action_create_payments()
                        total_paid += payment_amount

                    # Reconcile payments if fully paid
                    if total_paid >= invoice.amount_total:
                        invoice.action_post()
                        invoice.action_create_payments()
                        invoice.action_invoice_paid()

                    _logger.info(
                        f"Payments automatically managed for invoice {invoice.chargebee_id}. Total paid: {total_paid}"
                    )
                except chargebee.APIError as e:
                    _logger.error(
                        f"Error syncing payments for invoice {invoice.chargebee_id}: {e.json_obj}"
                    )
                except Exception as e:
                    _logger.error(
                        f"Error managing payments for invoice {invoice.chargebee_id}: {e}"
                    )

        return invoices

    def action_sync_credit_notes(self):
        """Sync only credit notes from Chargebee."""
        chargebee_config = self.env["chargebee.configuration"].search([], limit=1)
        if (
                not chargebee_config
                or not chargebee_config.api_key
                or not chargebee_config.site_name
        ):
            raise UserError(_("Chargebee configuration is incomplete."))

        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)
        try:
            _logger.info("Starting Chargebee credit note sync...")
            credit_notes = chargebee.CreditNote.list({"limit": 100})
            for credit_note_data in credit_notes:
                credit_note = credit_note_data.credit_note

                cn_company = self.env[
                    "res.company"
                ].get_or_create_company_from_chargebee(credit_note.business_entity_id)
                # Check if the credit note already exists
                existing_cn = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("chargebee_id", "=", credit_note.id),
                            ("company_id", "=", cn_company.id),
                        ],
                        limit=1,
                    )
                )
                if existing_cn:
                    _logger.info(
                        f"Credit note {existing_cn.name} already exists. Skipping."
                    )
                    continue

                # Prepare credit note lines
                credit_note_lines = [
                    (
                        0,
                        0,
                        {
                            "name": line.description,
                            "quantity": 1,
                            "price_unit": -(
                                    line.amount / 100
                            ),  # Negative for credit notes
                        },
                    )
                    for line in credit_note.line_items
                ]

                # Collect product IDs from credit note lines
                product_ids = []
                for line in credit_note.line_items:
                    product = self.env["product.product"].search(
                        [("default_code", "=", line.id)], limit=1
                    )
                    if product:
                        product_ids.append(product.id)

                cn_journal = self._get_credit_note_journal(chargebee_config, cn_company, product_ids)

                # Create credit note
                new_cn = (
                    self.env["account.move"]
                    .sudo()
                    .create(
                        {
                            "move_type": "out_refund",
                            "partner_id": self._get_or_create_partner(credit_note).id,
                            "chargebee_id": credit_note.id,
                            "invoice_date": fields.Datetime.to_string(
                                datetime.utcfromtimestamp(credit_note.date)
                            ),
                            "invoice_line_ids": credit_note_lines,
                            "company_id": cn_company.id,
                            "journal_id": cn_journal.id,
                        }
                    )
                )

            _logger.info("Credit note sync completed successfully.")
        except Exception as e:
            _logger.error(f"Error syncing credit notes: {e}")
            raise UserError(
                _(
                    "An error occurred while syncing credit notes. Please check the logs for details."
                )
            )

    def sync_credit_notes(self, invoice):
        """Fetch and sync credit notes related to an invoice."""
        try:
            _logger.info("➡️➡️ credit note sync invoked")
            if not invoice.chargebee_id:
                _logger.warning(
                    "Skipping credit note sync: missing Chargebee invoice ID for invoice %s",
                    invoice.name,
                )
                return

            credit_notes = chargebee.CreditNote.list(
                {"reference_invoice_id[is]": invoice.chargebee_id}
            )

            for credit_note_data in credit_notes:
                credit_note = credit_note_data.credit_note
                # Check if the credit note already exists
                existing_cn = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("chargebee_id", "=", credit_note.id),
                            ("company_id", "=", invoice.company_id.id),
                        ],
                        limit=1,
                    )
                )
                if not existing_cn:
                    # Prepare credit note lines
                    credit_note_lines = [
                        (
                            0,
                            0,
                            {
                                "name": line.description,
                                "quantity": 1,
                                "price_unit": -line.amount
                                              / 100,  # Negative for credit notes
                                "tax_ids": [],  # Populate tax_ids if applicable
                            },
                        )
                        for line in credit_note.line_items
                    ]

                    chargebee_config = self.env["chargebee.configuration"].search([], limit=1)
                    # Get product IDs from invoice lines
                    product_ids = invoice.invoice_line_ids.mapped('product_id').ids
                    cn_journal = self._get_credit_note_journal(chargebee_config, invoice.company_id, product_ids)

                    # Create credit note in Odoo
                    new_cn = self.env["account.move"].create(
                        {
                            "move_type": "out_refund",
                            "partner_id": invoice.partner_id.id,
                            "chargebee_id": credit_note.id,
                            "invoice_date": self.convert_timestamp_to_datetime(
                                credit_note.date
                            ),
                            "line_ids": credit_note_lines,
                            "company_id": invoice.company_id.id,
                            "journal_id": cn_journal.id,
                        }
                    )
                else:
                    _logger.info(
                        f"Credit note {credit_note.id} already exists for invoice {invoice.chargebee_id}."
                    )
        except chargebee.APIError as e:
            _logger.error(
                f"Error syncing credit notes for invoice {invoice.chargebee_id}: {e.json_obj}"
            )
            raise UserError(
                _("Failed to sync credit notes. Error: %s")
                % e.json_obj.get("message", str(e))
            )
        except Exception as e:
            _logger.error(
                f"Error syncing credit notes for invoice {invoice.chargebee_id}: {e}"
            )
            raise UserError(
                _(
                    "An error occurred while syncing credit notes. Please check the logs for details."
                )
            )

    def action_sync_account_invoices(self):
        """Sync invoices from Chargebee and create products if they do not exist."""
        chargebee_config = self.env["chargebee.configuration"].search([], limit=1)
        if (
                not chargebee_config
                or not chargebee_config.api_key
                or not chargebee_config.site_name
        ):
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        try:
            start_time = datetime.now()
            total_records = 0
            invoices = chargebee.Invoice.list({"limit": 100})
            for inv_data in invoices:
                invoice = inv_data.invoice

                # skipping subscription invoice
                # if invoice.subscription_id:
                #     _logger.info(f"Skipping subscription invoice with id {invoice.id}")
                #     continue

                invoice_company = self.env[
                    "res.company"
                ].get_or_create_company_from_chargebee(invoice.business_entity_id)
                # Check if the invoice already exists
                existing_invoice = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("chargebee_id", "=", invoice.id),
                            ("company_id", "=", invoice_company.id),
                        ],
                        limit=1,
                    )
                )
                if existing_invoice and existing_invoice.state == "posted":
                    _logger.info(
                        f"Skipping reconciled invoice: {existing_invoice.name}"
                    )
                    continue

                # Prepare line items and create products if needed
                line_items = []
                for item in getattr(invoice, "line_items", []):
                    # Check if the product exists
                    product = self.env["product.product"].search(
                        [
                            ("default_code", "=", item.id),
                            ("company_id", "=", invoice_company.id),
                        ],
                        limit=1,
                    )
                    if not product:
                        # Create product if it doesn't exist
                        product = (
                            self.env["product.product"]
                            .sudo()
                            .create(
                                {
                                    "name": item.description or "Chargebee Product",
                                    "default_code": item.id,
                                    "list_price": item.unit_amount
                                                  / 100,  # Default price from Chargebee
                                    "type": "service",  # Or 'consu'/'product' based on your needs
                                    "company_id": invoice_company.id,
                                    "taxes_id": [(6, 0, [])],
                                    "supplier_taxes_id": [(6, 0, [])],
                                }
                            )
                        )
                        _logger.info(
                            f"Created product {product.name} with Chargebee ID {item.id}."
                        )

                    # Prepare the line item
                    line_items.append(
                        (
                            0,
                            0,
                            {
                                "name": item.description or "Chargebee Item",
                                "quantity": item.quantity,
                                "price_unit": item.unit_amount
                                              / 100,  # Convert cents to currency
                                "product_id": product.id,
                            },
                        )
                    )

                # Collect product IDs from line items
                product_ids = [line[2]['product_id'] for line in line_items if line[2].get('product_id')]
                invoice_journal = self._get_invoice_journal(chargebee_config, invoice_company, product_ids)

                if not invoice_journal:
                    raise UserError(
                        _(
                            "No Sales journal found for company '%s', sync companies first and Create one with default income account."
                        )
                        % invoice_company.name
                    )

                if not invoice_journal.default_account_id:
                    raise UserError(
                        _(
                            "No Default Account set for journal '%s'. Set default account for this journal"
                        )
                        % invoice_journal.name
                    )

                # Prepare invoice values
                vals = {
                    "move_type": "out_invoice",
                    "invoice_date": self.convert_timestamp_to_datetime(invoice.date),
                    "partner_id": self._get_or_create_partner(invoice).id,
                    "chargebee_id": invoice.id,
                    "invoice_line_ids": line_items,
                    "fiscal_position_id": False,
                    "company_id": invoice_company.id,
                    "journal_id": invoice_journal.id,
                }
                # Create or update invoice
                if existing_invoice and existing_invoice.state != "cancel":
                    try:
                        existing_invoice.write(vals)
                        # odoo_invoice = existing_invoice
                    except Exception as e:
                        _logger.warning(
                            f"Could not update reconciled invoice {existing_invoice.name}: {e}"
                        )
                        odoo_invoice = self.sudo().create(vals)  # ← Also add this
                        super(AccountMove, odoo_invoice).action_post()
                else:
                    odoo_invoice = self.sudo().create(vals)
                    super(AccountMove, odoo_invoice).action_post()
                    self.env.cr.commit()
                    total_records += 1

                # Handle linked payments for paid invoices
                if invoice.status == "paid" and invoice.linked_payments and odoo_invoice:
                    self._register_chargebee_payment(
                        odoo_invoice, invoice.linked_payments
                    )
                    self.env.cr.commit()
            # Log successful data processing
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                table_name="Account Invoice",
                record_count=total_records,
                status="success",
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                cr_configuration_id=chargebee_config.id,
                context="invoices",  # Specify context for this page
            )

        except Exception as e:
            _logger.error(f"Error syncing invoices: {e}")
            # Log the failure of data processing
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                table_name="Account Invoice",
                record_count=total_records,
                status="failure",
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                cr_configuration_id=chargebee_config.id,
                error_message=str(e),
                context="invoices",  # Specify context for this page
            )
            raise UserError(
                _(
                    "An error occurred while syncing invoices. Please check the logs for details."
                )
            )

    def _register_chargebee_payment(self, odoo_invoice, linked_payments):
        """Register payments for a synced Chargebee invoice."""
        _logger.info("registering payment")

        # Check if invoice is already paid or has nothing to pay
        if odoo_invoice.payment_state in ('paid', 'in_payment'):
            _logger.info(f"Invoice {odoo_invoice.name} is already paid, skipping payment registration")
            return

        if odoo_invoice.amount_residual <= 0:
            _logger.info(f"Invoice {odoo_invoice.name} has no residual amount, skipping payment registration")
            return

        _logger.info("invoice company while registering payment : %s", odoo_invoice.company_id)

        chargebee_config = self.env["chargebee.configuration"].search([], limit=1)

        # Get product IDs from invoice lines
        product_ids = odoo_invoice.invoice_line_ids.mapped('product_id').ids
        invoice_payment_journal = self._get_payment_journal(
            chargebee_config,
            odoo_invoice.company_id,
            product_ids
        )

        # Ensure we have a valid journal
        if not invoice_payment_journal:
            _logger.error(f"No payment journal found for company {odoo_invoice.company_id.name}")
            return

        for payment_data in linked_payments:
            _logger.info("➡️➡️➡️ payment data : %s", payment_data)

            # Check remaining amount before each payment
            if odoo_invoice.amount_residual <= 0:
                _logger.info(f"Invoice {odoo_invoice.name} is fully paid, skipping remaining payments")
                break

            # Handle both dict and object formats
            if isinstance(payment_data, dict):
                payment_date = self.convert_timestamp_to_datetime(
                    payment_data.get('txn_date')
                )
                payment_amount = payment_data.get('applied_amount', 0) / 100.0
            else:
                payment_date = self.convert_timestamp_to_datetime(
                    payment_data.txn_date
                )
                payment_amount = payment_data.applied_amount / 100.0

            # Don't register payment if amount is 0 or exceeds residual
            if payment_amount <= 0:
                _logger.warning(f"Skipping payment with amount {payment_amount}")
                continue

            # Cap payment amount to residual amount
            payment_amount = min(payment_amount, odoo_invoice.amount_residual)

            payment_vals = {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": odoo_invoice.partner_id.id,
                "amount": payment_amount,
                "currency_id": odoo_invoice.currency_id.id,
                "payment_date": payment_date,
                "journal_id": invoice_payment_journal.id,
                "communication": odoo_invoice.name,
            }

            try:
                # Register the payment with proper context - Odoo 17 syntax
                payment_register = (
                    self.env["account.payment.register"]
                    .with_context(
                        active_model="account.move",
                        active_ids=odoo_invoice.ids,
                    )
                    .sudo()
                    .create(payment_vals)
                )

                # Verify company is set properly before creating payment
                if not payment_register.company_id:
                    _logger.error(f"Payment register has no company set for invoice {odoo_invoice.name}")
                    continue

                # Create and post the payment
                _logger.info('creating payment')
                _logger.info("payment : %s", payment_register)
                _logger.info("payment company : %s", payment_register.company_id.name)
                payment_register.action_create_payments()

                _logger.info(
                    f"Registered and reconciled payment for invoice {odoo_invoice.name}: {payment_vals}"
                )
            except Exception as e:
                _logger.error(
                    f"Failed to register payment for invoice {odoo_invoice.name}: {e}"
                )

    def sync_subscription_from_chargebee(self):
        """Sync Chargebee Subscription as Invoice in Odoo"""
        chargebee_config = self.env["chargebee.configuration"].search([], limit=1)
        if (
                not chargebee_config
                or not chargebee_config.api_key
                or not chargebee_config.site_name
        ):
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        try:
            start_time = datetime.now()
            total_records = 0
            subscriptions = chargebee.Subscription.list({"limit": 100})

            for sub_data in subscriptions:
                subscription = sub_data.subscription

                # Skipping non-active subscriptions
                if subscription.status != "active":
                    _logger.info(
                        f"Skipping non-active subscription with id {subscription.id}"
                    )
                    continue

                # Fetch customer details for partner creation
                customer = chargebee.Customer.retrieve(subscription.customer_id)

                subs_company = self.env[
                    "res.company"
                ].get_or_create_company_from_chargebee(subscription.business_entity_id)

                # Check if the invoice already exists (assuming a 'chargebee_subscription_id' field on account.move)
                existing_invoice = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("chargebee_id", "=", subscription.id),
                            ("company_id", "=", subs_company.id),
                        ],
                        limit=1,
                    )
                )
                if existing_invoice and existing_invoice.state == "posted":
                    _logger.info(
                        f"Skipping posted subscription invoice: {existing_invoice.name}"
                    )
                    continue

                quotes = chargebee.Quote.list({"subscription_id[is]": subscription.id})
                # quote = quotes[0]
                for quote in quotes:
                    total_cycles = self.fetch_total_cycles_of_the_subscription(quote)
                    # Prepare line items and create products if needed
                    line_items = []
                    for item in getattr(subscription, "subscription_items", []):
                        # Check if the product exists
                        product = self.env["product.product"].search(
                            [
                                ("default_code", "=", item.item_price_id),
                                ("company_id", "=", subs_company.id),
                            ],
                            limit=1,
                        )
                        if not product:
                            # Create product if it doesn't exist
                            product = (
                                self.env["product.product"]
                                .sudo()
                                .create(
                                    {
                                        "name": item.item_price_id
                                                or "Chargebee Subscription Product",
                                        "default_code": item.item_price_id,
                                        "list_price": item.unit_price
                                                      / 100,  # Assuming smallest currency unit (e.g., paise/cents)
                                        "type": "service",  # Or 'consu'/'product' based on your needs
                                        "company_id": subs_company.id,
                                        "taxes_id": [(6, 0, [])],
                                    }
                                )
                            )
                            _logger.info(
                                f"Created product {product.name} with Chargebee Item Price ID {item.item_price_id}."
                            )

                        # Prepare the line item
                        line_items.append(
                            (
                                0,
                                0,
                                {
                                    "name": item.item_price_id
                                            or "Chargebee Subscription Item",
                                    "quantity": item.quantity * total_cycles,
                                    "price_unit": item.unit_price
                                                  / 100,  # Convert smallest unit to currency
                                    "product_id": product.id,
                                    "deferred_start_date": self.convert_timestamp_to_date_for_deffered(
                                        quote.quoted_ramp.line_items[0].start_date
                                    ),
                                    "deferred_end_date": self.convert_timestamp_to_date_for_deffered(
                                        quote.quoted_ramp.line_items[0].end_date
                                    ),
                                },
                            )
                        )

                    # Collect product IDs from line items
                    product_ids = [line[2]['product_id'] for line in line_items if line[2].get('product_id')]
                    invoice_journal = self._get_invoice_journal(chargebee_config, subs_company, product_ids)

                    if not invoice_journal:
                        raise UserError(
                            _(
                                "No Sales journal found for company '%s' sync companies first and Create one Sales journal with default income account."
                            )
                            % subs_company.name
                        )

                    if not invoice_journal.default_account_id:
                        raise UserError(
                            _(
                                "No Default Account set for journal '%s'. Set default account for this journal"
                            )
                            % invoice_journal.name
                        )

                    # Prepare invoice values
                    vals = {
                        "move_type": "out_invoice",
                        "invoice_date": self.convert_timestamp_to_datetime(
                            subscription.started_at
                        ),
                        "partner_id": self.create_partner_for_subscription(
                            subscription
                        ).id,
                        "chargebee_id": subscription.id,
                        "invoice_line_ids": line_items,
                        "fiscal_position_id": False,
                        "company_id": subs_company.id,
                        "journal_id": invoice_journal.id,
                    }
                    # Create or update invoice
                    if existing_invoice:
                        try:
                            existing_invoice.write(vals)
                        except Exception as e:
                            _logger.warning(
                                f"Could not update posted subscription invoice {existing_invoice.name}: {e}"
                            )
                    else:
                        odoo_invoice = self.sudo().create(vals)
                        super(AccountMove, odoo_invoice).action_post()
                    self.env.cr.commit()
                    total_records += 1

            # Log successful data processing
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                table_name="Subscription",
                record_count=total_records,
                status="success",
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                cr_configuration_id=chargebee_config.id,
                context="subscriptions",  # Specify context for this page
            )

        except Exception as e:
            _logger.error(f"Error syncing subscriptions: {e}")
            # Log the failure of data processing
            self.env["cr.data.processing.log"].sudo()._log_data_processing(
                table_name="Subscription",
                record_count=total_records,
                status="failure",
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                cr_configuration_id=chargebee_config.id,
                error_message=str(e),
                context="subscriptions",  # Specify context for this page
            )
            raise UserError(
                _(
                    "An error occurred while syncing subscriptions. Please check the logs for details."
                )
            )

    def _get_or_create_partner(self, invoice):
        """Fetch or create a partner based on Chargebee invoice data."""
        billing_address = getattr(invoice, "billing_address", None)
        full_name = f"{getattr(billing_address, 'first_name', '')} {getattr(billing_address, 'last_name', '')}".strip()
        partner = self.env["res.partner"].search([("name", "=", full_name)], limit=1)

        if not partner:
            partner = (
                self.env["res.partner"]
                .sudo()
                .create(
                    {
                        "name": full_name,
                        "phone": getattr(billing_address, "phone", ""),
                        "street": getattr(billing_address, "street", ""),
                        "city": getattr(billing_address, "city", ""),
                        "zip": getattr(billing_address, "zip", ""),
                        "country_id": self.env["res.country"]
                        .sudo()
                        .search(
                            [("name", "=", getattr(billing_address, "country", ""))],
                            limit=1,
                        )
                        .id,
                        "company_id": self.env["res.company"]
                        .get_or_create_company_from_chargebee(
                            invoice.business_entity_id
                        )
                        .id,
                    }
                )
            )
        return partner

    def create_partner_for_subscription(self, invoice):
        """Fetch or create a partner based on Chargebee invoice data."""
        billing_address = getattr(invoice, "billing_address", None)
        full_name = f"Subscription Partner"
        partner = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": full_name,
                    "phone": getattr(billing_address, "phone", ""),
                    "street": getattr(billing_address, "street", ""),
                    "city": getattr(billing_address, "city", ""),
                    "zip": getattr(billing_address, "zip", ""),
                    "country_id": self.env["res.country"]
                    .sudo()
                    .search(
                        [("name", "=", getattr(billing_address, "country", ""))],
                        limit=1,
                    )
                    .id,
                    "company_id": self.env["res.company"]
                    .get_or_create_company_from_chargebee(invoice.business_entity_id)
                    .id,
                }
            )
        )
        return partner

    # Webhook methods
    def sync_invoice_from_webhook_data(self, invoice_data, webhook_content=None):
        """
        Process and create/update invoice from Chargebee webhook data.
        This method reuses existing logic to minimize code duplication.

        Args:
            invoice_data (dict): Invoice data from Chargebee webhook
            webhook_content (dict): Full webhook content (optional)

        Returns:
            account.move: Created or updated invoice record
        """
        try:
            _logger.info("➡️➡️ invoice data : %s", invoice_data)
            invoice_id = invoice_data.get('id')
            subscription_id = invoice_data.get('subscription_id')
            business_entity_id = invoice_data.get('business_entity_id')

            # Get or create company based on business entity
            invoice_company = self.env['res.company'].get_or_create_company_from_chargebee(
                business_entity_id
            )

            # Check if invoice already exists
            existing_invoice = self.sudo().search([
                ('chargebee_id', '=', invoice_id),
                ('company_id', '=', invoice_company.id)
            ], limit=1)

            _logger.info("➡️➡️ existing_invoice : %s", existing_invoice)

            # Skip if invoice is already posted (don't modify posted invoices)
            if existing_invoice and existing_invoice.state == 'posted':
                _logger.info(f"Invoice {existing_invoice.name} already posted, skipping update")
                return existing_invoice

            # **ADD THIS: Skip if invoice is being created right now in another transaction**
            if existing_invoice and existing_invoice.state == 'draft':
                _logger.info(f"Invoice {existing_invoice.name} already exists in draft, returning it")
                return existing_invoice

            # Prepare line items
            line_items = self._prepare_invoice_lines_from_webhook(
                invoice_data.get('line_items', []),
                invoice_company
            )
            _logger.info("➡️➡️ Line Items : %s", line_items)

            if not line_items:
                _logger.warning(f"No line items found for invoice {invoice_id}")
                return None

            # Get appropriate journal
            chargebee_config = self.env['chargebee.configuration'].search([], limit=1)

            # Collect product IDs from prepared line items
            product_ids = [line[2]['product_id'] for line in line_items if line[2].get('product_id')]
            invoice_journal = self._get_invoice_journal(chargebee_config, invoice_company, product_ids)

            _logger.info("➡️➡️ invoice journal : %s", invoice_journal)

            if not invoice_journal or not invoice_journal.default_account_id:
                raise UserError(
                    _("Sales journal not properly configured for company '%s'") % invoice_company.name
                )

            # Get or create partner
            partner = self._get_or_create_partner_from_webhook(invoice_data, invoice_company)

            # Prepare invoice values
            invoice_vals = {
                'move_type': 'out_invoice',
                'invoice_date': self.convert_timestamp_to_datetime(invoice_data.get('date')),
                'partner_id': partner.id,
                'chargebee_id': invoice_id,
                'chargebee_invoice_url': invoice_data.get('pdf_url', ''),
                'invoice_line_ids': line_items,
                'fiscal_position_id': False,
                'company_id': invoice_company.id,
                'journal_id': invoice_journal.id,
                'ref': f"Subscription: {subscription_id}" if subscription_id else None,
            }

            # Create or update invoice
            if existing_invoice:
                existing_invoice.write(invoice_vals)
                odoo_invoice = existing_invoice
                _logger.info(f"Updated existing invoice: {odoo_invoice.name}")
            else:
                odoo_invoice = self.sudo().create(invoice_vals)
                # Post the invoice
                super(AccountMove, odoo_invoice).action_post()
                _logger.info(f"Created new invoice: {odoo_invoice.name}")

            self.env.cr.commit()

            # Handle payments if invoice is paid
            if invoice_data.get('status') == 'paid':
                self._process_webhook_payments(odoo_invoice, invoice_data, webhook_content)

            return odoo_invoice

        except Exception as e:
            _logger.error(f"Error syncing invoice from webhook: {str(e)}", exc_info=True)
            self.env.cr.rollback()
            raise

    def _prepare_invoice_lines_from_webhook(self, line_items, company):
        """
        Prepare invoice lines from webhook line items data.

        Args:
            line_items (list): Line items from Chargebee webhook
            company (res.company): Company record

        Returns:
            list: Invoice line items in Odoo format
        """
        prepared_lines = []

        for item in line_items:
            # Get or create product
            product = self._get_or_create_product_from_webhook(item, company)
            _logger.info("❌❌ item data : %s", item)

            if not product:
                _logger.warning(f"Could not create product for item: {item.get('id')}")
                continue

            line_val = (0, 0, {
                'name': item.get('description') or 'Chargebee Item',
                'quantity': item.get('quantity', 1),
                'price_unit': item.get('unit_amount', 0) / 100,  # Convert cents to currency
                'product_id': product.id,
                'tax_ids': [],  # Add tax logic if needed
                'deferred_start_date': self.convert_timestamp_to_date_for_deffered(item['date_from']),
                'deferred_end_date': self.convert_timestamp_to_date_for_deffered(item['date_to']),
            })
            prepared_lines.append(line_val)

        return prepared_lines

    def _get_or_create_product_from_webhook(self, item_data, company):
        """
        Get or create product from webhook item data.

        Args:
            item_data (dict): Line item data
            company (res.company): Company record

        Returns:
            product.product: Product record
        """
        item_id = item_data.get('entity_id') or item_data.get('id')

        # Search for existing product
        product = self.env['product.product'].search([
            ('default_code', '=', item_id),
            ('company_id', '=', company.id)
        ], limit=1)

        if not product:
            # Create new product
            product = self.env['product.product'].sudo().create({
                'name': item_data.get('description') or f"Chargebee Item {item_id}",
                'default_code': item_id,
                'list_price': item_data.get('unit_amount', 0) / 100,
                'type': 'service',
                'company_id': company.id,
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            })
            _logger.info(f"Created product {product.name} from webhook")

        return product

    def _get_or_create_partner_from_webhook(self, invoice_data, company):
        """
        Get or create partner from webhook invoice data.
        Reuses existing _get_or_create_partner logic.

        Args:
            invoice_data (dict): Invoice data from webhook
            company (res.company): Company record

        Returns:
            res.partner: Partner record
        """
        # Try to get customer data from webhook
        customer_id = invoice_data.get('customer_id')

        # Search by Chargebee customer ID first
        if customer_id:
            partner = self.env['res.partner'].search([
                ('chargebee_customer_id', '=', customer_id)
            ], limit=1)

            if partner:
                return partner

        # Fallback: Create from billing address if available
        billing_address = invoice_data.get('billing_address', {})

        if billing_address:
            first_name = billing_address.get('first_name', '')
            last_name = billing_address.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip() or "Chargebee Customer"

            # Search by name
            partner = self.env['res.partner'].search([('name', '=', full_name)], limit=1)

            if not partner:
                # Create new partner
                partner = self.env['res.partner'].sudo().create({
                    'name': full_name,
                    'chargebee_customer_id': customer_id,
                    'phone': billing_address.get('phone', ''),
                    'email': billing_address.get('email', ''),
                    'street': billing_address.get('line1', ''),
                    'street2': billing_address.get('line2', ''),
                    'city': billing_address.get('city', ''),
                    'zip': billing_address.get('zip', ''),
                    'state_id': False,  # Add state mapping if needed
                    'country_id': self.env['res.country'].sudo().search([
                        ('code', '=', billing_address.get('country', ''))
                    ], limit=1).id,
                    'company_id': company.id,
                })
                _logger.info(f"Created partner {partner.name} from webhook")
        else:
            # Create generic partner if no billing address
            partner = self.env['res.partner'].sudo().create({
                'name': 'Chargebee Customer',
                'chargebee_customer_id': customer_id,
                'company_id': company.id,
            })

        return partner

    def _get_invoice_journal(self, chargebee_config, company, product_ids=None):
        """
        Get appropriate invoice journal based on company and product family.

        Args:
            chargebee_config (chargebee.configuration): Chargebee config
            company (res.company): Company record
            product_ids (list): List of product IDs (optional)

        Returns:
            account.journal: Journal record
        """
        _logger.info("❌❌ product_ids : %s", product_ids)
        # Get item family from products if provided
        item_family = None
        if product_ids:
            products = self.env['product.product'].sudo().browse(product_ids)
            # Get the first product's family (all products in same invoice should have same family)
            for product in products:
                _logger.info("❌❌ product family id : %s", product.product_tmpl_id.item_family_id)
                if product.product_tmpl_id.item_family_id:
                    item_family = product.product_tmpl_id.item_family_id
                    break

        # Find journal config matching both company and family (if family exists)
        if item_family:
            _logger.info("❌❌ Item Family found : %s", item_family)
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id and r.item_family_id.id == item_family.id
            )[:1]
        else:
            _logger.info("❌❌ Item Family not found : %s", item_family)
            # Fallback to company-only match
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id
            )[:1]

        invoice_journal = (
            journal_config.invoice_journal_id
            if journal_config and journal_config.invoice_journal_id
            else self.env['account.journal'].sudo().search([
                ('type', '=', 'sale'),
                ('company_id', '=', company.id)
            ], limit=1)
        )
        _logger.info("❌❌ Invoice journal : %s", invoice_journal)

        return invoice_journal

    def _get_payment_journal(self, chargebee_config, company, product_ids=None):
        """
        Get appropriate payment journal based on company and product family.

        Args:
            chargebee_config (chargebee.configuration): Chargebee config
            company (res.company): Company record
            product_ids (list): List of product IDs (optional)

        Returns:
            account.journal: Payment journal record
        """
        # Get item family from products if provided
        _logger.info("❌❌ product_ids : %s", product_ids)
        item_family = None
        if product_ids:
            products = self.env['product.product'].sudo().browse(product_ids)
            for product in products:
                if product.product_tmpl_id.item_family_id:
                    item_family = product.product_tmpl_id.item_family_id
                    break

        # Find journal config matching both company and family (if family exists)
        if item_family:
            _logger.info("❌❌ Item Family found : %s", item_family)
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id and r.item_family_id.id == item_family.id
            )[:1]
        else:
            # Fallback to company-only match
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id
            )[:1]

        payment_journal = (
            journal_config.invoice_payment_journal_id
            if journal_config and journal_config.invoice_payment_journal_id
            else self.env['account.journal'].sudo().search([
                ('type', '=', 'bank'),
                ('company_id', '=', company.id)
            ], limit=1)
        )

        return payment_journal

    def _get_credit_note_journal(self, chargebee_config, company, product_ids=None):
        """
        Get appropriate credit note journal based on company and product family.

        Args:
            chargebee_config (chargebee.configuration): Chargebee config
            company (res.company): Company record
            product_ids (list): List of product IDs (optional)

        Returns:
            account.journal: Credit note journal record
        """
        # Get item family from products if provided
        item_family = None
        if product_ids:
            products = self.env['product.product'].sudo().browse(product_ids)
            for product in products:
                if product.product_tmpl_id.item_family_id:
                    item_family = product.product_tmpl_id.item_family_id
                    break

        # Find journal config matching both company and family (if family exists)
        if item_family:
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id and r.item_family_id.id == item_family.id
            )[:1]
        else:
            # Fallback to company-only match
            journal_config = chargebee_config.journal_config_ids.filtered(
                lambda r: r.company_id.id == company.id
            )[:1]

        credit_note_journal = (
            journal_config.credit_note_journal_id
            if journal_config and journal_config.credit_note_journal_id
            else self.env['account.journal'].sudo().search([
                ('type', '=', 'sale'),
                ('company_id', '=', company.id)
            ], limit=1)
        )

        return credit_note_journal

    def _process_webhook_payments(self, odoo_invoice, invoice_data, webhook_content):
        """
        Process payments from webhook data.

        Args:
            odoo_invoice (account.move): Invoice record
            invoice_data (dict): Invoice data from webhook
            webhook_content (dict): Full webhook content
        """
        try:
            _logger.info("🎯 processing payment... ")
            # Check if there are linked payments
            linked_payments = invoice_data.get('linked_payments', [])
            _logger.info("➡️➡️ Linked Payments : %s", linked_payments)

            # Also check for transaction in webhook content (for payment_succeeded event)
            if webhook_content and webhook_content.get('transaction'):
                transaction = webhook_content.get('transaction')
                _logger.info("Transaction from webhook : %s", webhook_content.get('transaction'))
                # Convert transaction to linked_payment format
                linked_payment = type('obj', (object,), {
                    'txn_date': transaction.get('date'),
                    'applied_amount': transaction.get('amount'),
                })()
                linked_payments = [linked_payment]

            _logger.info("➡️➡️ below linked payments : %s", linked_payments)

            if linked_payments:
                _logger.info(f"Processing {len(linked_payments)} payments for invoice {odoo_invoice.name}")
                self._register_chargebee_payment(odoo_invoice, linked_payments)
                self.env.cr.commit()

        except Exception as e:
            _logger.error(f"Error processing webhook payments: {str(e)}", exc_info=True)

