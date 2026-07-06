# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Odoo Stripe Refund Manager | Invoice Payment Refund & Credit Note Automation",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "https://www.creyox.com/helpdesk",
    "live_test_url": "https://www.creyox.com/helpdesk?module_tech_name=cr_stripe_refund_payment&version=17.0",
    "category": "Accounting",
    "summary": """
    Process Stripe invoice payment refunds directly from Odoo with full or partial refund support. 
    Automatically generate credit notes, sync refund records with Stripe, and manage refund workflows 
    securely without leaving the Odoo backend.
    """,
    "license": "OPL-1",
    "version": "17.0.0.0",
    "description": """
    <h1>Stripe Refund Payment for Odoo – Invoice Refund & Credit Note Automation</h1>
    <p>The Stripe Refund Payment module for Odoo allows businesses to process Stripe payment refunds directly from the Odoo backend. Users can initiate full or partial refunds for invoice payments without logging into Stripe, ensuring a faster and more efficient refund workflow. The module automatically creates credit notes, syncs refund data with Stripe, and maintains accurate financial records inside Odoo.</p>
    
    <h2>Key Features</h2>
    <ul>
    <li>Refund Stripe invoice payments directly from Odoo</li>
    <li>Process full or partial refunds with a few clicks</li>
    <li>Securely handle Stripe refund transactions</li>
    <li>Automatic credit note creation for refunded amounts</li>
    <li>View and track Stripe refund history inside Odoo</li>
    <li>Prevent refunds exceeding the original payment amount</li>
    <li>Keep Stripe and Odoo refund records synchronized</li>
    </ul>
    
    <h2>Benefits</h2>
    <ul>
    <li>Eliminates the need to log in to Stripe for refunds</li>
    <li>Reduces manual work and prevents refund errors</li>
    <li>Ensures accurate accounting with automatic credit notes</li>
    <li>Improves refund processing speed and efficiency</li>
    <li>Maintains clear financial records within Odoo</li>
    </ul>
    
    <h2>Why Choose This Stripe Refund Integration?</h2>
    <p>This module provides a seamless and secure way to manage Stripe payment refunds directly inside Odoo. Businesses can quickly process refunds, maintain accurate accounting records, and improve operational efficiency while keeping all refund data synchronized between Stripe and Odoo.</p>
    
    <h2>Related Apps</h2>
    <ul>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_miro_odoo_integration">Odoo Miro Connector</a></li>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_gelato_odoo_integration">Odoo To Gelato Integration</a></li>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_nacex_odoo_integration">Nacex Shipping Integration</a></li>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_mydsv_odoo">MYDSV Shipping Integration</a></li>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_bigcommerce_odoo_integration">Advanced Odoo BigCommerce Connector</a></li>
    <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_bigquerrys_odoo_integration">Advanced Odoo BigCommerce Connector</a></li>
    </ul>
    
    <p>For custom Odoo integrations and CRM enhancements, visit <a href="https://creyox.com">Creyox Technologies</a></p>
    <p>Watch the youtube video, visit <a href="https://www.youtube.com/@CreyoxTechnologies">Creyox Technologies YouTube Videos</a></p>
    <p>Read our blog post, visit <a href="https://www.creyox.com/blog">Creyox Technologies Blogs</a></p>
    """,
    "depends": ["base", "payment_stripe", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/payment_refund_wiz.xml"
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "price": 49,
    "currency": "USD",
}