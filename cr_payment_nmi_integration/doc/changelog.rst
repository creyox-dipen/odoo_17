17.0.0.2(Date: 28th May,2026)
-------------------------------

- Integrated NMI with custom ACH/Card payment forms, support for credit/debit card transaction fees, and card tokenization for secure future payments.
- Also added fee line on invoice when payment through invoice preview.

17.0.0.3(Date: 10th September,2026)
-----------------------------------

 - [ADD] Added real-time order summary sidebar updates on card BIN lookup and saved token selection.
 - [ADD] Displayed formatted fee badges next to saved payment tokens on checkout page.
 - [FIX] Resolved cart validation update error during checkout transaction creation when surcharge fee lines are added.
 - [FIX] Prevented duplicate surcharge fee line creation on sales orders and invoices.
 - [ADD] Added QWeb template inheritance for website_sale.total to render the surcharge line item in the Order Summary.
 - [FIX] Updated JS DOM manipulation to target Odoo 17 elements (#cart_total, #cart_products, #amount_total_summary).