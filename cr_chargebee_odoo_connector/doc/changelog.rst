17.0.0.2(Date: 08th July,2026)
-------------------------------
- Synced invoices maintain the same invoice number as in Chargebee instead of standard Odoo sequence.
- Synced invoices fetch and attach the corresponding Chargebee PDF invoice to Odoo's chatter.
- Added automatic webhook processing for real-time sync of Product Families, Products, and Customers.
- Added multi-company tax configuration setting to assign and apply company-wise taxes under product Customer Taxes.
- Synced customers are created as Company type with their Chargebee billing VAT mapped to the Odoo Tax ID (VAT) field.
