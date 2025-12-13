# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import chargebee
from datetime import datetime, timezone
import logging
import json
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    chargebee_id = fields.Char(string="Chargebee Invoice ID", help="ID of the invoice in Chargebee")
    chargebee_invoice_url = fields.Char(string="Chargebee Invoice URL", help="Link to the invoice in Chargebee")
    linked_payments = fields.Text(string="Linked Payments", help="Details of linked payments stored as JSON")
    adjustments = fields.Text(string="Adjustments", help="Adjustment credit notes stored as JSON")

    def convert_timestamp_to_datetime(self, timestamp):
        """Convert a timestamp to a datetime object."""
        if timestamp:
            return fields.Datetime.to_string(datetime.utcfromtimestamp(timestamp))
        return None

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
        print("Start : ",start)
        print("End : ",end)
        delta = relativedelta(end, start)
        print("delta : ",delta)
        if billing_period_unit == 'month':
            total_months = delta.years * 12 + delta.months
            print("Delta years : ",delta.years)
            print("Delta months : ",delta.months)
            print("total months : ",total_months)
            return total_months // billing_period

        if billing_period_unit == 'year':
            total_years = delta.years
            return total_years // billing_period

        if billing_period_unit == 'week':
            total_days = (end - start).days
            return total_days // (billing_period * 7)

        if billing_period_unit == 'day':
            total_days = (end - start).days
            return total_days // billing_period

        raise ValueError(f"Unsupported billing_period_unit: {billing_period_unit}")

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super(AccountMove, self).create(vals_list)
        chargebee_config = self.env['chargebee.configuration'].search([], limit=1)

        if not chargebee_config or not chargebee_config.api_key or not chargebee_config.site_name:
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        for invoice in invoices:
            if invoice.chargebee_id:
                try:
                    # Skip reconciled invoices
                    if invoice._is_reconciled():
                        _logger.info(f"Skipping reconciled invoice: {invoice.chargebee_id}")
                        continue

                    # Sync credit notes
                    self.sync_credit_notes(invoice)

                    # Fetch payment details from Chargebee
                    payments = chargebee.Transaction.list({"invoice_id": invoice.chargebee_id})
                    total_paid = 0

                    for payment_data in payments:
                        payment = payment_data.transaction
                        payment_date = self.convert_timestamp_to_datetime(payment.date)
                        payment_amount = payment.amount / 100  # Convert cents to currency

                        # create payment in user selected journal
                        invoice_payment_journal_line = chargebee_config.journal_config_ids.filtered(
                            lambda r: r.company_id.id == invoice.company_id.id
                        )[:1]
                        invoice_payment_journal = (
                            invoice_payment_journal_line.invoice_payment_journal_id
                            if invoice_payment_journal_line.invoice_payment_journal_id
                            else self.env['account.journal'].sudo().search(
                                [('type', '=', 'bank'), ('company_id', '=', invoice.company_id.id)], limit=1)
                        )

                        # Create payment in Odoo
                        payment_vals = {
                            'partner_id': invoice.partner_id.id,
                            'amount': payment_amount,
                            'date': payment_date,
                            'payment_type': 'inbound',
                            'journal_id': invoice_payment_journal.id,
                            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                            'communication': f"Chargebee Payment: {payment.id}",
                            'move_id': invoice.id,
                        }
                        odoo_payment = self.env['account.payment.register'].create(payment_vals)
                        odoo_payment.action_post()
                        odoo_payment.action_create_payments()
                        total_paid += payment_amount

                    # Reconcile payments if fully paid
                    if total_paid >= invoice.amount_total:
                        invoice.action_post()
                        invoice.action_create_payments()
                        invoice.action_invoice_paid()

                    _logger.info(
                        f"Payments automatically managed for invoice {invoice.chargebee_id}. Total paid: {total_paid}")
                except chargebee.APIError as e:
                    _logger.error(f"Error syncing payments for invoice {invoice.chargebee_id}: {e.json_obj}")
                except Exception as e:
                    _logger.error(f"Error managing payments for invoice {invoice.chargebee_id}: {e}")

        return invoices

    def action_sync_credit_notes(self):
        """Sync only credit notes from Chargebee."""
        chargebee_config = self.env['chargebee.configuration'].search([], limit=1)
        if not chargebee_config or not chargebee_config.api_key or not chargebee_config.site_name:
            raise UserError(_("Chargebee configuration is incomplete."))

        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)
        try:
            _logger.info("Starting Chargebee credit note sync...")
            credit_notes = chargebee.CreditNote.list()
            for credit_note_data in credit_notes:
                credit_note = credit_note_data.credit_note

                # Check if the credit note already exists
                existing_cn = self.env['account.move'].search([('chargebee_id', '=', credit_note.id)], limit=1)
                if existing_cn:
                    _logger.info(f"Credit note {existing_cn.name} already exists. Skipping.")
                    continue

                # Prepare credit note lines
                credit_note_lines = [
                    (0, 0, {
                        'name': line.description,
                        'quantity': 1,
                        'price_unit': -(line.amount / 100),  # Negative for credit notes
                    })
                    for line in credit_note.line_items
                ]

                cn_company = self.env['res.company'].get_or_create_company_from_chargebee(
                    credit_note.business_entity_id)
                cn_journal_line = chargebee_config.journal_config_ids.filtered(
                    lambda r: r.company_id.id == cn_company.id
                )[:1]
                cn_journal = (
                    cn_journal_line.credit_note_journal_id
                    if cn_journal_line.credit_note_journal_id
                    else self.env['account.journal'].sudo().search(
                        [('type', '=', 'sale'), ('company_id', '=', cn_company.id)], limit=1)
                )

                # Create credit note
                new_cn = self.env['account.move'].sudo().create({
                    'move_type': 'out_refund',
                    'partner_id': self._get_or_create_partner(credit_note).id,
                    'chargebee_id': credit_note.id,
                    'invoice_date': fields.Datetime.to_string(datetime.utcfromtimestamp(credit_note.date)),
                    'invoice_line_ids': credit_note_lines,
                    'company_id': cn_company.id,
                    'journal_id': cn_journal.id
                })

            _logger.info("Credit note sync completed successfully.")
        except Exception as e:
            _logger.error(f"Error syncing credit notes: {e}")
            raise UserError(_("An error occurred while syncing credit notes. Please check the logs for details."))

    def sync_credit_notes(self, invoice):
        """Fetch and sync credit notes related to an invoice."""
        print("sync credit note function called")
        try:
            credit_notes = chargebee.CreditNote.list({"invoice_id": invoice.chargebee_id})
            for credit_note_data in credit_notes:
                credit_note = credit_note_data.credit_note

                # Check if the credit note already exists
                existing_cn = self.env['account.move'].search([('chargebee_id', '=', credit_note.id)], limit=1)

                if not existing_cn:
                    # Prepare credit note lines
                    credit_note_lines = [
                        (0, 0, {
                            'name': line.description,
                            'quantity': 1,
                            'price_unit': line.amount / 100,  # Negative for credit notes
                            'tax_ids': [],  # Populate tax_ids if applicable
                        })
                        for line in credit_note.line_items
                    ]

                    chargebee_config = self.env['chargebee.configuration'].search([], limit=1)
                    cn_journal_line = chargebee_config.journal_config_ids.filtered(
                        lambda r: r.company_id.id == invoice.company_id.id
                    )[:1]
                    cn_journal = (
                        cn_journal_line.credit_note_journal_id
                        if cn_journal_line.credit_note_journal_id
                        else self.env['account.journal'].sudo().search(
                            [('type', '=', 'sale'), ('company_id', '=', invoice.company_id.id)], limit=1)
                    )

                    # Create credit note in Odoo
                    self.env['account.move'].create({
                        'move_type': 'out_refund',
                        'partner_id': invoice.partner_id.id,
                        'chargebee_id': credit_note.id,
                        'invoice_date': self.convert_timestamp_to_datetime(credit_note.date),
                        'line_ids': credit_note_lines,
                        'company_id': invoice.company_id.id,
                        'journal_id': cn_journal.id,
                    })
                else:
                    _logger.info(f"Credit note {credit_note.id} already exists for invoice {invoice.chargebee_id}.")
        except chargebee.APIError as e:
            _logger.error(f"Error syncing credit notes for invoice {invoice.chargebee_id}: {e.json_obj}")
            raise UserError(_("Failed to sync credit notes. Error: %s") % e.json_obj.get('message', str(e)))
        except Exception as e:
            _logger.error(f"Error syncing credit notes for invoice {invoice.chargebee_id}: {e}")
            raise UserError(_("An error occurred while syncing credit notes. Please check the logs for details."))

    def action_sync_account_invoices(self):
        """Sync invoices from Chargebee and create products if they do not exist."""
        chargebee_config = self.env['chargebee.configuration'].search([], limit=1)
        if not chargebee_config or not chargebee_config.api_key or not chargebee_config.site_name:
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        try:
            start_time = datetime.now()
            total_records = 0
            invoices = chargebee.Invoice.list()
            for inv_data in invoices:
                invoice = inv_data.invoice

                # skipping subscription invoice
                if invoice.subscription_id:
                    _logger.info(f"Skipping subscription invoice with id {invoice.id}")
                    continue

                invoice_company = self.env['res.company'].get_or_create_company_from_chargebee(
                    invoice.business_entity_id)

                # Check if the invoice already exists
                existing_invoice = self.search([('chargebee_id', '=', invoice.id)], limit=1)
                if existing_invoice and existing_invoice.state == 'posted':
                    _logger.info(f"Skipping reconciled invoice: {existing_invoice.name}")
                    continue

                # Prepare line items and create products if needed
                line_items = []
                for item in getattr(invoice, 'line_items', []):
                    # Check if the product exists
                    product = self.env['product.product'].search([('default_code', '=', item.id)], limit=1)
                    if not product:
                        # Create product if it doesn't exist
                        product = self.env['product.product'].sudo().create({
                            'name': item.description or "Chargebee Product",
                            'default_code': item.id,
                            'list_price': item.unit_amount / 100,  # Default price from Chargebee
                            'type': 'service',  # Or 'consu'/'product' based on your needs
                            'company_id': invoice_company.id
                        })
                        _logger.info(f"Created product {product.name} with Chargebee ID {item.id}.")

                    # Prepare the line item
                    line_items.append((0, 0, {
                        'name': item.description or "Chargebee Item",
                        'quantity': item.quantity,
                        'price_unit': item.unit_amount / 100,  # Convert cents to currency
                        'product_id': product.id,
                    }))

                journal_config = chargebee_config.journal_config_ids
                invoice_journal_line = journal_config.filtered(
                    lambda r: r.company_id.id == invoice_company.id
                )[:1]
                invoice_journal = (
                    invoice_journal_line.invoice_journal_id
                    if invoice_journal_line.invoice_journal_id
                    else self.env['account.journal'].sudo().search(
                        [('type', '=', 'sale'), ('company_id', '=', invoice_company.id)], limit=1)
                )
                if not invoice_journal:
                    raise UserError(
                        _("No Sales journal found for company '%s'. Create one with default income account.") % invoice_company.name)

                if not invoice_journal.default_account_id:
                    raise UserError(
                        _("No Default Account set for journal '%s'. Set default account for this journal") % invoice_journal.name)

                # Prepare invoice values
                vals = {
                    'move_type': 'out_invoice',
                    'invoice_date': self.convert_timestamp_to_datetime(invoice.date),
                    'partner_id': self._get_or_create_partner(invoice).id,
                    'chargebee_id': invoice.id,
                    'invoice_line_ids': line_items,
                    'company_id': invoice_company.id,
                    'journal_id': invoice_journal.id,
                }
                # Create or update invoice
                if existing_invoice:
                    print("invoice is existing...")
                    try:
                        existing_invoice.write(vals)
                    except Exception as e:
                        _logger.warning(f"Could not update reconciled invoice {existing_invoice.name}: {e}")
                else:
                    print("invoice doesnt exist")
                    odoo_invoice = self.sudo().create(vals)
                    print("new created invoice : ", odoo_invoice)
                    super(AccountMove, odoo_invoice).action_post()
                    print("invoice is posting...")
                self.env.cr.commit()
                total_records += 1

                # Handle linked payments for paid invoices
                if invoice.status == 'paid' and invoice.linked_payments:
                    self._register_chargebee_payment(odoo_invoice, invoice.linked_payments)
                    self.env.cr.commit()
            # Log successful data processing
            self.env['cr.data.processing.log'].sudo()._log_data_processing(
                table_name='Account Invoice',
                record_count=total_records,
                status='success',
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                cr_configuration_id=chargebee_config.id,
                context='invoices',  # Specify context for this page
            )

        except Exception as e:
            _logger.error(f"Error syncing invoices: {e}")
            # Log the failure of data processing
            self.env['cr.data.processing.log'].sudo()._log_data_processing(
                table_name='Account Invoice',
                record_count=total_records,
                status='failure',
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                cr_configuration_id=chargebee_config.id,
                error_message=str(e),
                context='invoices',  # Specify context for this page
            )
            raise UserError(_("An error occurred while syncing invoices. Please check the logs for details."))

    def _register_chargebee_payment(self, odoo_invoice, linked_payments):
        """Register payments for a synced Chargebee invoice."""
        PaymentRegister = self.env['account.payment.register']
        chargebee_config = self.env['chargebee.configuration'].search([], limit=1)
        print("in payment : ", odoo_invoice)

        # fetching invoice payment journal selected by user on CB configuration
        invoice_payment_journal_line = chargebee_config.journal_config_ids.filtered(
            lambda r: r.company_id.id == odoo_invoice.company_id.id
        )[:1]
        invoice_payment_journal = (
            invoice_payment_journal_line.invoice_payment_journal_id
            if invoice_payment_journal_line.invoice_payment_journal_id
            else self.env['account.journal'].sudo().search(
                [('type', '=', 'bank'), ('company_id', '=', odoo_invoice.company_id.id)], limit=1)
        )
        print("350")
        for payment_data in linked_payments:
            payment_date = self.convert_timestamp_to_datetime(payment_data.txn_date)  # Convert timestamp to date
            payment_amount = payment_data.applied_amount / 100.0  # Convert cents to base currency
            payment_vals = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': odoo_invoice.partner_id.id,
                'amount': payment_amount,  # Set the payment amount
                'currency_id': odoo_invoice.currency_id.id,
                'payment_date': payment_date,  # Set the payment date
                'journal_id': invoice_payment_journal.id,
                'company_id': odoo_invoice.company_id.id,
                'communication': odoo_invoice.name,
                # 'invoice_ids': [(6, 0, [odoo_invoice.id])],  # Link the invoice
            }
            print("Payment vals : ", payment_vals)
            try:
                # Register the payment with proper context
                payment_register = self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=odoo_invoice.id
                ).create(payment_vals)
                print("Payment register : ", payment_register)
                # Create and post the payment
                payment_register.action_create_payments()

                _logger.info(f"Registered and reconciled payment for invoice {odoo_invoice.name}: {payment_vals}")
            except Exception as e:
                _logger.error(f"Failed to register payment for invoice {odoo_invoice.name}: {e}")

    def sync_subscription_from_chargebee(self):
        """Sync Chargebee Subscription as Invoice in Odoo"""
        chargebee_config = self.env['chargebee.configuration'].search([], limit=1)
        if not chargebee_config or not chargebee_config.api_key or not chargebee_config.site_name:
            raise UserError(_("Chargebee configuration is incomplete."))

        # Configure Chargebee
        chargebee.configure(chargebee_config.api_key, chargebee_config.site_name)

        try:
            start_time = datetime.now()
            total_records = 0
            subscriptions = chargebee.Subscription.list()

            for sub_data in subscriptions:
                subscription = sub_data.subscription

                # Skipping non-active subscriptions
                if subscription.status != 'active':
                    _logger.info(f"Skipping non-active subscription with id {subscription.id}")
                    continue

                # Fetch customer details for partner creation
                customer = chargebee.Customer.retrieve(subscription.customer_id)

                invoice_company = self.env['res.company'].get_or_create_company_from_chargebee(
                    subscription.business_entity_id)

                # Check if the invoice already exists (assuming a 'chargebee_subscription_id' field on account.move)
                existing_invoice = self.env["account.move"].with_company(invoice_company.id).search([('chargebee_id', '=', subscription.id)], limit=1)
                print("Existing invoice : ",existing_invoice)
                if existing_invoice or existing_invoice.state == 'posted':
                    _logger.info(f"Skipping posted subscription invoice: {existing_invoice.name}")
                    continue

                quotes = chargebee.Quote.list({"subscription_id[is]": subscription.id})
                quote = quotes[0]
                total_cycles = self.fetch_total_cycles_of_the_subscription(quote)

                # Prepare line items and create products if needed
                line_items = []
                for item in getattr(subscription, 'subscription_items', []):
                    # Check if the product exists
                    product = self.env['product.product'].search([('default_code', '=', item.item_price_id)], limit=1)
                    if not product:
                        # Create product if it doesn't exist
                        product = self.env['product.product'].sudo().create({
                            'name': item.item_price_id or "Chargebee Subscription Product",
                            'default_code': item.item_price_id,
                            'list_price': item.unit_price / 100,  # Assuming smallest currency unit (e.g., paise/cents)
                            'type': 'service',  # Or 'consu'/'product' based on your needs
                            'company_id': invoice_company.id
                        })
                        _logger.info(
                            f"Created product {product.name} with Chargebee Item Price ID {item.item_price_id}.")

                    # Prepare the line item
                    line_items.append((0, 0, {
                        'name': item.item_price_id or "Chargebee Subscription Item",
                        'quantity': item.quantity * total_cycles,
                        'price_unit': item.unit_price / 100,  # Convert smallest unit to currency
                        'product_id': product.id,
                        'deferred_start_date': self.convert_timestamp_to_datetime(quote.quoted_ramp.line_items[0].start_date),
                        'deferred_end_date': self.convert_timestamp_to_datetime(quote.quoted_ramp.line_items[0].end_date),
                    }))

                # Calculate Total subscription Price


                invoice_journal_line = chargebee_config.journal_config_ids.filtered(
                    lambda r: r.company_id.id == invoice_company.id
                )[:1]
                invoice_journal = (
                    invoice_journal_line.invoice_journal_id
                    if invoice_journal_line.invoice_journal_id
                    else self.env['account.journal'].sudo().search(
                        [('type', '=', 'sale'), ('company_id', '=', invoice_company.id)], limit=1)
                )

                print("invoice journal : ", invoice_journal, invoice_journal.sudo().name)
                if not invoice_journal:
                    raise UserError(
                        _("No Sales journal found for company '%s'. Create one with default income account.") % invoice_company.name)

                if not invoice_journal.default_account_id:
                    raise UserError(
                        _("No Default Account set for journal '%s'. Set default account for this journal") % invoice_journal.name)

                # Prepare invoice values
                vals = {
                    'move_type': 'out_invoice',
                    'invoice_date': self.convert_timestamp_to_datetime(subscription.started_at),
                    'partner_id': self._get_or_create_partner(subscription).id,
                    'chargebee_id': subscription.id,
                    'invoice_line_ids': line_items,
                    'company_id': invoice_company.id,
                    'journal_id': invoice_journal.id,
                }
                print("invoice vals : ", vals)
                # Create or update invoice
                if existing_invoice:
                    print("invoice is existing...")
                    try:
                        existing_invoice.write(vals)
                    except Exception as e:
                        _logger.warning(f"Could not update posted subscription invoice {existing_invoice.name}: {e}")
                else:
                    print("invoice doesnt exist")
                    odoo_invoice = self.sudo().create(vals)
                    print("new created invoice : ", odoo_invoice)
                    super(AccountMove, odoo_invoice).action_post()
                    print("invoice is posting...")
                self.env.cr.commit()
                total_records += 1

            # Log successful data processing
            self.env['cr.data.processing.log'].sudo()._log_data_processing(
                table_name='Account Invoice',
                record_count=total_records,
                status='success',
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                cr_configuration_id=chargebee_config.id,
                context='subscriptions',  # Specify context for this page
            )

        except Exception as e:
            _logger.error(f"Error syncing subscriptions: {e}")
            # Log the failure of data processing
            self.env['cr.data.processing.log'].sudo()._log_data_processing(
                table_name='Account Invoice',
                record_count=total_records,
                status='failure',
                timespan=str(datetime.now() - start_time),
                initiated_at=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                cr_configuration_id=chargebee_config.id,
                error_message=str(e),
                context='subscriptions',  # Specify context for this page
            )
            raise UserError(_("An error occurred while syncing subscriptions. Please check the logs for details."))

        print("Syncing Subscription to invoice")

    def _get_or_create_partner(self, invoice):
        """Fetch or create a partner based on Chargebee invoice data."""
        billing_address = getattr(invoice, 'billing_address', None)
        full_name = f"{getattr(billing_address, 'first_name', '')} {getattr(billing_address, 'last_name', '')}".strip()
        partner = self.env['res.partner'].search([('name', '=', full_name)], limit=1)

        if not partner:
            partner = self.env['res.partner'].sudo().create({
                'name': full_name,
                'phone': getattr(billing_address, 'phone', ''),
                'street': getattr(billing_address, 'street', ''),
                'city': getattr(billing_address, 'city', ''),
                'zip': getattr(billing_address, 'zip', ''),
                'country_id': self.env['res.country'].search([('name', '=', getattr(billing_address, 'country', ''))],
                                                             limit=1).id,
                'company_id': self.env['res.company'].get_or_create_company_from_chargebee(
                    invoice.business_entity_id).id
            })
            print("partner : ", partner)
        return partner
