# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import http, _
from odoo.http import request
import logging
import json
import hmac
import hashlib

_logger = logging.getLogger(__name__)


class ChargebeeWebhookController(http.Controller):
    """
    Controller to handle Chargebee webhook callbacks for subscription installment invoices.

    Webhook endpoint: /chargebee/webhook

    Supported Events:
    - invoice_generated: When a new subscription invoice is generated
    - payment_succeeded: When a payment is successfully processed
    - invoice_updated: When invoice is updated
    """

    @http.route('/chargebee/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def chargebee_webhook(self):
        """
        Main webhook endpoint to receive Chargebee events.

        Returns:
            dict: Response with status and message
        """
        try:

            # Get Chargebee configuration
            config = request.env['chargebee.configuration'].sudo().search([], limit=1)

            if not config:
                _logger.warning(
                    "Chargebee configuration not found while creating subscription invoice from chargebee...")
                return

            # CRITICAL CHECK: Only process if webhook is enabled
            if not config.webhook_enabled:
                _logger.info("Webhook processing for chargebee is disabled in configuration. Skipping.")
                return

            # Get webhook payload
            raw_body = request.httprequest.data
            webhook_data = json.loads(raw_body)

            if not webhook_data:
                _logger.error("Chargebee webhook: Empty payload received")
                return

            # Extract event details
            event_type = webhook_data.get('event_type')
            content = webhook_data.get('content', {})

            _logger.info(f"Chargebee webhook received: {event_type}")

            # Process only subscription invoice related events
            if event_type in ['invoice_generated', 'payment_succeeded', 'invoice_updated']:
                self._process_invoice_webhook(event_type, content)

            else:
                _logger.info(f"Chargebee webhook: Event type '{event_type}' not handled")
                return

        except Exception as e:
            _logger.error(f"Chargebee webhook error: {str(e)}", exc_info=True)
            return

    def _process_invoice_webhook(self, event_type, content):
        """
        Process invoice-related webhook events.

        Args:
            event_type (str): Type of webhook event
            content (dict): Webhook content data

        Returns:
            dict: Response with status and message
        """
        try:
            invoice_data = content.get('invoice')

            if not invoice_data:
                _logger.error(f"Chargebee webhook: No invoice data in {event_type}")
                return {"status": "error", "message": "No invoice data"}

            invoice_id = invoice_data.get('id')
            subscription_id = invoice_data.get('subscription_id')

            # Only process subscription invoices (installment invoices)
            if not subscription_id:
                _logger.info(f"Chargebee webhook: Invoice {invoice_id} is not a subscription invoice, skipping")
                return {"status": "ignored", "message": "Not a subscription invoice"}

            _logger.info(f"Processing subscription invoice {invoice_id} for event {event_type}")

            _logger.info("👉 Event Type : %s", event_type)
            # Process based on event type
            if event_type == 'invoice_generated':
                result = self._handle_invoice_generated(invoice_data, content)
            elif event_type == 'payment_succeeded':
                result = self._handle_payment_succeeded(invoice_data, content)
            elif event_type == 'invoice_updated':
                result = self._handle_invoice_updated(invoice_data, content)
            else:
                result = {"status": "ignored", "message": "Event not handled"}

            return result

        except Exception as e:
            _logger.error(f"Error processing invoice webhook: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _handle_invoice_generated(self, invoice_data, content):
        """
        Handle invoice_generated event - Create new subscription installment invoice.

        Args:
            invoice_data (dict): Invoice data from webhook
            content (dict): Full webhook content

        Returns:
            dict: Response with status
        """
        try:
            _logger.info("🎯 Handling Invoice Generated")
            # Use existing method from account.move to sync invoice
            AccountMove = request.env['account.move'].sudo()

            # Process the invoice using existing sync method
            odoo_invoice = AccountMove.sync_invoice_from_webhook_data(invoice_data, content)

            if odoo_invoice:
                _logger.info(f"Successfully created/updated invoice {odoo_invoice.name} from webhook")
                return {
                    "status": "success",
                    "message": f"Invoice {odoo_invoice.name} processed",
                    "invoice_id": odoo_invoice.id
                }
            else:
                return {"status": "error", "message": "Failed to create invoice"}

        except Exception as e:
            _logger.error(f"Error handling invoice_generated: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _handle_payment_succeeded(self, invoice_data, content):
        """
        Handle payment_succeeded event - Register payment for invoice.

        Args:
            invoice_data (dict): Invoice data from webhook
            content (dict): Full webhook content including transaction

        Returns:
            dict: Response with status
        """
        try:
            _logger.info("🎯 Handling Payment Succeeded")
            invoice_id = invoice_data.get('id')
            AccountMove = request.env['account.move'].sudo()

            # Find existing invoice with a small delay to allow invoice_generated to complete
            odoo_invoice = AccountMove.search([('chargebee_id', '=', invoice_id)], limit=1)
            _logger.info("👉👉 odoo invoice for payment : %s", odoo_invoice)
            # If invoice doesn't exist, wait a moment and try again (race condition handling)
            if not odoo_invoice:
                _logger.info("👉👉 invoice is not found for payment")
                import time
                time.sleep(0.9)  # Wait 900ms for invoice_generated event to complete
                odoo_invoice = AccountMove.search([('chargebee_id', '=', invoice_id)], limit=1)

            if not odoo_invoice:
                _logger.info("👉👉 creating invoice for payment")
                _logger.warning(f"Invoice {invoice_id} not found in Odoo, creating it first")
                # Create invoice first if it doesn't exist
                odoo_invoice = AccountMove.sync_invoice_from_webhook_data(invoice_data, content)

            if odoo_invoice:
                # Get transaction/payment data
                transaction_data = content.get('transaction')

                if transaction_data:
                    # Register payment using existing method
                    AccountMove._register_chargebee_payment(
                        odoo_invoice,
                        [transaction_data]  # Wrap in list as existing method expects list
                    )

                    _logger.info(f"Payment registered for invoice {odoo_invoice.name}")
                    return {
                        "status": "success",
                        "message": f"Payment registered for {odoo_invoice.name}"
                    }
                else:
                    _logger.warning(f"No transaction data in payment_succeeded webhook")
                    return {"status": "warning", "message": "No transaction data"}
            else:
                return {"status": "error", "message": "Invoice not found"}

        except Exception as e:
            _logger.error(f"Error handling payment_succeeded: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _handle_invoice_updated(self, invoice_data, content):
        """
        Handle invoice_updated event - Update existing invoice.

        Args:
            invoice_data (dict): Invoice data from webhook
            content (dict): Full webhook content

        Returns:
            dict: Response with status
        """
        try:
            _logger.info("🎯 Handling Invoice Update")
            invoice_id = invoice_data.get('id')
            AccountMove = request.env['account.move'].sudo()

            # Find existing invoice
            odoo_invoice = AccountMove.search([('chargebee_id', '=', invoice_id)], limit=1)

            if odoo_invoice:
                # Update invoice using existing sync method
                updated_invoice = AccountMove.sync_invoice_from_webhook_data(invoice_data, content)

                _logger.info(f"Invoice {odoo_invoice.name} updated from webhook")
                return {
                    "status": "success",
                    "message": f"Invoice {odoo_invoice.name} updated"
                }
            else:
                # Invoice doesn't exist, create it
                _logger.info(f"Invoice {invoice_id} not found, creating new invoice")
                odoo_invoice = AccountMove.sync_invoice_from_webhook_data(invoice_data, content)

                if odoo_invoice:
                    return {
                        "status": "success",
                        "message": f"Invoice {odoo_invoice.name} created"
                    }
                else:
                    return {"status": "error", "message": "Failed to create invoice"}

        except Exception as e:
            _logger.error(f"Error handling invoice_updated: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}