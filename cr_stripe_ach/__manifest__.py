# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Odoo Stripe ACH Direct Debit Payment Integration for Invoices | Secure Bank Transfer via Stripe",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "https://www.creyox.com/helpdesk",
    "live_test_url": "https://www.creyox.com/helpdesk?module_tech_name=cr_stripe_ach&version=17.0",
    "category": "Accounting",
    "summary": """
    Enable secure ACH Direct Debit payments for Odoo invoices using Stripe. 
    Automatically collect USD bank transfer payments from US customers, update 
    invoice status in real time, and streamline invoice payment processing with 
    full Stripe ACH integration.
    """,
    "license": "OPL-1",
    "version": "17.0.0.0",
    "description": """
    <h1>Stripe ACH Direct Debit Payments for Odoo Invoices</h1>
    <p>The Stripe ACH Invoice Integration for Odoo allows US-based businesses to collect invoice payments directly through ACH Direct Debit using Stripe. Customers can securely pay invoices using their US bank account, while Stripe automatically confirms the transaction and updates the invoice payment status in Odoo. This integration eliminates manual payment tracking and provides a seamless, automated workflow for invoice payment collection.</p>

    <h2>Key Features</h2>
    <ul>
    <li>Pay Odoo invoices directly through ACH bank transfer</li>
    <li>Automated invoice payment confirmation via Stripe</li>
    <li>Real-time payment status updates from Stripe</li>
    <li>Secure bank account payments using Stripe ACH</li>
    <li>Quick and simple ACH payment process for customers</li>
    <li>Fully integrated Stripe ACH payment workflow</li>
    <li>Easy configuration inside the Odoo backend</li>
    <li>Supports USD transactions and US bank accounts</li>
    </ul>

    <h2>Benefits</h2>
    <ul>
    <li>Automates invoice payment collection through ACH</li>
    <li>Reduces manual reconciliation and payment tracking</li>
    <li>Provides secure bank transfer payments for customers</li>
    <li>Speeds up invoice payment processing</li>
    <li>Improves financial accuracy and workflow efficiency</li>
    </ul>

    <h2>Why Choose Stripe ACH Integration for Odoo?</h2>
    <p>This module provides a secure and automated ACH Direct Debit solution for collecting invoice payments through Stripe. Businesses operating in the US can streamline their billing workflow, reduce manual payment handling, and ensure accurate invoice reconciliation while offering customers a convenient bank transfer payment method.</p>

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
        "views/account_move_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "price": 69,
    "currency": "USD",
}
