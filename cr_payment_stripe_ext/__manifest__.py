# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    "name": "Advanced Stripe Backend Payment Integration – Pay Invoices from Odoo Backend",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "https://www.creyox.com/helpdesk",
    "live_test_url": "https://www.creyox.com/helpdesk?module_tech_name=cr_payment_stripe_ext&version=17.0",
    "category": "Accounting",
    "summary": """
    Enable secure Stripe card payments directly from Odoo backend invoices. Automate invoice validation, reduce errors, and speed up collections.
    """,
    "license": "OPL-1",
    "version": "17.0.0.0",
    "description": """
    <h1>Advanced Stripe Backend Invoice Payment Integration for Odoo</h1>

        <p class="lead">
        The <b>#1 Stripe backend payment solution for Odoo</b> that lets finance teams <b>pay customer invoices directly from the backend</b>—securely, instantly, and without portal dependency.
        </p>
        
        <blockquote>
        Stop switching tools. Stop manual reconciliation. With this Stripe backend integration, invoice payments are completed in seconds—right where your accounting team works.
        </blockquote>
        
        <h2>Overview</h2>
        <p>
        By default, Odoo’s Stripe integration is limited to online portal payments. This module <b>extends Stripe integration into the Odoo backend</b>, allowing admins and authorized users to <b>pay invoices directly from the invoice form</b> using Stripe.
        </p>
        
        <p>
        With a single click on <b>“Pay with Stripe”</b>, users are redirected to Stripe’s secure checkout to complete card payments. Once successful, the invoice is automatically updated, payment is recorded, and reconciliation happens instantly—<b>zero manual effort</b>.
        </p>
        
        <h2>Key Features</h2>
        <ul>
          <li><i class="fa fa-check"></i> <b>Backend Invoice Payments with Stripe</b></li>
          <li><i class="fa fa-check"></i> <b>Pay Directly from Invoice Form View</b></li>
          <li><i class="fa fa-check"></i> <b>Supports Major Cards</b> (Visa, MasterCard, AmEx & more)</li>
          <li><i class="fa fa-check"></i> <b>Secure Stripe Checkout Redirection</b></li>
          <li><i class="fa fa-check"></i> <b>Automated Invoice Status Update</b></li>
          <li><i class="fa fa-check"></i> <b>Real-Time Stripe Payment Status Sync</b></li>
          <li><i class="fa fa-check"></i> <b>Role-Based Access Control</b></li>
        </ul>
        
        <h2>Detailed Features</h2>
        
        <p><b>Stripe Backend Integration</b><br/>
        Process customer payments using Stripe directly from Odoo’s backend—no website or customer portal required.</p>
        
        <p><b>One-Click “Pay with Stripe” Button</b><br/>
        Authorized users can initiate payments instantly from the invoice form view, improving operational speed.</p>
        
        <p><b>Automated Accounting Accuracy</b><br/>
        Once payment is completed, Odoo automatically marks the invoice as paid and records the transaction details.</p>
        
        <p><b>Secure & Compliant Checkout</b><br/>
        Payments are handled through Stripe’s PCI-compliant hosted checkout, ensuring maximum security.</p>
        
        <p><b>Access Control & User Permissions</b><br/>
        Restrict payment initiation to admins or selected internal users for complete financial control.</p>
        
        <h3>FAQs</h3>
        
        <p><b>Q1: Can payments be done without the customer portal?</b><br/>
        Yes. This module enables Stripe payments directly from the Odoo backend invoice screen.</p>
        
        <p><b>Q2: Which cards are supported?</b><br/>
        All major cards supported by Stripe, including Visa, MasterCard, American Express, and more.</p>
        
        <p><b>Q3: Is the invoice updated automatically after payment?</b><br/>
        Absolutely. The invoice is automatically marked as paid, and payment details are recorded instantly.</p>
        
        <p><b>Q4: Can I control who sees the “Pay with Stripe” button?</b><br/>
        Yes. Role-based access ensures only authorized users can initiate payments.</p>
        
        <h2>Why Choose Us?</h2>
        <ul>
          <li><i class="fa fa-star"></i> Built to outperform default Odoo Stripe limitations</li>
          <li><i class="fa fa-star"></i> Production-tested & accounting-safe</li>
          <li><i class="fa fa-star"></i> Clean UI that feels native to Odoo</li>
          <li><i class="fa fa-star"></i> Fast support & regular updates</li>
          <li><i class="fa fa-star"></i> Trusted by businesses using Stripe at scale</li>
        </ul>
        
        <hr/>
        
        <p>
        For custom Odoo integrations and CRM enhancements, visit <a href="https://www.creyox.com" target="_blank">Creyox Technologies</a>
        </p>
        
        <p>
        Watch the youtube video, visit <a href="https://www.youtube.com/@CreyoxTechnologies" target="_blank">Creyox Technologies YouTube Videos</a>
        </p>
        
        <p>
        Read our blog post, visit <a href="https://www.creyox.com/blogs" target="_blank">Creyox Technologies Blogs</a>
        </p>
        
        <p>
        Visit Our Linkedin Page <a href="https://www.linkedin.com/company/creyox-technologies" target="_blank">Creyox Technologies Linkedin Page</a>
        </p>
    """,
    "depends": ["base", "payment_stripe", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/payment_access.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "price": 49,
    "currency": "USD",
}
