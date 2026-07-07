# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import http, _
from odoo.http import request
import logging
import json
import hmac
import hashlib
import chargebee

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

            # Process webhook events
            if event_type in ['invoice_generated', 'payment_succeeded', 'invoice_updated']:
                self._process_invoice_webhook(event_type, content)
            elif event_type in ['customer_created', 'customer_changed']:
                self._process_customer_webhook(event_type, content)
            elif event_type in ['item_created', 'item_updated']:
                self._process_item_webhook(event_type, content)
            elif event_type in ['item_family_created', 'item_family_updated']:
                self._process_item_family_webhook(event_type, content)
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
                time.sleep(3.5)  # Wait 900ms for invoice_generated event to complete
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

    def _process_customer_webhook(self, event_type, content):
        """Process customer webhook events to create/update res.partner records."""
        try:
            customer_data = content.get('customer')
            if not customer_data:
                _logger.info("No customer data found in webhook payload")
                return {"status": "error", "message": "No customer data"}

            customer_id = customer_data.get('id')
            first_name = customer_data.get('first_name', '')
            last_name = customer_data.get('last_name', '')
            email = customer_data.get('email')
            phone = customer_data.get('phone')
            company_name = customer_data.get('company')
            business_entity_id = customer_data.get('business_entity_id')

            customer_company = request.env['res.company'].sudo().get_or_create_company_from_chargebee(business_entity_id)

            ResPartner = request.env['res.partner'].sudo()
            existing_partner = ResPartner.search([
                ('chargebee_customer_id', '=', customer_id),
                ('company_id', '=', customer_company.id)
            ], limit=1)

            partner_name = f"{first_name} {last_name}".strip() or email or customer_id
            partner_vals = {
                'name': partner_name,
                'email': email,
                'phone': phone,
                'company_name': company_name,
                'chargebee_customer_id': customer_id,
                'company_id': customer_company.id,
                'is_company': True,
            }

            if existing_partner:
                existing_partner.write(partner_vals)
                _logger.info("Successfully updated Customer %s from webhook", partner_name)
            else:
                ResPartner.create(partner_vals)
                _logger.info("Successfully created Customer %s from webhook", partner_name)

            return {"status": "success"}
        except Exception as e:
            _logger.info("Error processing customer webhook: %s", str(e))
            return {"status": "error", "message": str(e)}

    def _process_item_webhook(self, event_type, content):
        """Process item webhook events to create/update product.template records."""
        try:
            item_data = content.get('item')
            if not item_data:
                _logger.info("No item data found in webhook payload")
                return {"status": "error", "message": "No item data"}
                
            item_id = item_data.get('id')
            item_name = item_data.get('external_name') or item_data.get('name')
            item_family_id = item_data.get('item_family_id')
            item_description = item_data.get('description', '')

            # Fetch config for API client
            config = request.env['chargebee.configuration'].sudo().search([], limit=1)
            price = 0.0
            currency = 'USD'
            if config and config.api_key and config.site_name:
                chargebee.configure(config.api_key, config.site_name)
                try:
                    item_prices = chargebee.ItemPrice.list({"item_id[is]": item_id, "limit": 1})
                    if item_prices:
                        item_price_data = item_prices[0].item_price
                        price = item_price_data.price / 100 if item_price_data.price else 0.0
                        currency = item_price_data.currency_code or 'USD'
                except Exception as e:
                    _logger.info("Could not fetch item price for item %s: %s", item_id, str(e))

            # Find associated family
            family = request.env['chargebee.item.family'].sudo().search([('chargebee_id', '=', item_family_id)], limit=1)

            # Get or create category
            category = request.env['product.category'].sudo().search([('id', '=', family.id)], limit=1) if family else False
            if not category:
                category = request.env['product.category'].sudo().create({
                    'name': family.name if family else 'Default Category'
                })

            ProductTemplate = request.env['product.template'].sudo()
            existing_product = ProductTemplate.search([('default_code', '=', item_id)], limit=1)

            vals = {
                'name': item_name,
                'list_price': price,
                'default_code': item_id,
                'description_sale': item_description or '',
                'description': item_description or '',
                'categ_id': category.id,
                'currency_id': request.env['res.currency'].sudo().search([('name', '=', currency)], limit=1).id,
                'company_id': False,
                'chargebee_id': item_id,
                'chargebee_created': True,
                'item_family_id': family.id if family else False,
                'taxes_id': [(5, 0, 0)],
                'supplier_taxes_id': [(5, 0, 0)],
            }

            if existing_product:
                existing_product.write(vals)
                _logger.info("Successfully updated Product %s from webhook", item_name)
            else:
                vals['type'] = 'consu'
                vals['detailed_type'] = 'consu'
                new_product = ProductTemplate.create(vals)
                new_product.write({
                    'taxes_id': [(5, 0, 0)],
                    'supplier_taxes_id': [(5, 0, 0)]
                })
                _logger.info("Successfully created Product %s from webhook", item_name)

            return {"status": "success"}
        except Exception as e:
            _logger.info("Error processing item webhook: %s", str(e))
            return {"status": "error", "message": str(e)}

    def _process_item_family_webhook(self, event_type, content):
        """Process item family webhook events to create/update chargebee.item.family records."""
        try:
            family_data = content.get('item_family')
            if not family_data:
                _logger.info("No item_family data found in webhook payload")
                return {"status": "error", "message": "No item_family data"}

            family_id = family_data.get('id')
            family_name = family_data.get('name')

            ChargebeeItemFamily = request.env['chargebee.item.family'].sudo()
            existing_family = ChargebeeItemFamily.search([('chargebee_id', '=', family_id)], limit=1)

            vals = {
                'name': family_name,
                'chargebee_id': family_id,
            }

            if existing_family:
                existing_family.write(vals)
                _logger.info("Successfully updated Item Family %s from webhook", family_name)
            else:
                ChargebeeItemFamily.create(vals)
                _logger.info("Successfully created Item Family %s from webhook", family_name)

            return {"status": "success"}
        except Exception as e:
            _logger.info("Error processing item family webhook: %s", str(e))
            return {"status": "error", "message": str(e)}