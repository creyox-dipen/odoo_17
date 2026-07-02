# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "BigQuery Odoo Integration | Google BigQuery Integration for Odoo – Two-Way Sync, Automation & Analytics",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Extra Tools",
    "summary": """
    	The BigQuery Odoo Connector enables seamless two-way data synchronization between 
    	Odoo and Google BigQuery, supporting real-time updates, scheduled syncs, and 
    	multi-company environments. Businesses can export sales, CRM, inventory, accounting, 
    	and other key Odoo records into BigQuery for advanced analytics, BI dashboards, and 
    	centralized reporting. With custom filters, dynamic table selection, and partial field sync, 
    	users gain full control over what data is transferred. The connector also allows importing 
    	selected BigQuery data back into Odoo, ensuring every department works with accurate, up-to-date 
    	information. Automated workflows, comprehensive logging, and easy configuration make it ideal for 
    	companies looking to streamline data pipelines, eliminate manual exports, and improve decision-making 
    	with powerful BigQuery analytics.
        """,
    "license": "OPL-1",
    "external_dependencies": {"python": ["google-cloud-bigquery", "google-auth"]},
    "version": "17.0.0.5",
    "description": """
    	 <h1>Odoo BigQuery Connector – Real-Time Sync, Automated Data Export/Import & Advanced Analytics</h1>
        <p>
            The Odoo BigQuery Connector provides seamless, secure, and automated two-way data synchronization 
            between Odoo and Google BigQuery. It enables businesses to export and import selected fields across 
            Sales, CRM, Inventory, Accounting, Projects, and custom modules directly into BigQuery for 
            advanced analytics, BI dashboards, machine learning, and centralized reporting. 
            With real-time sync, scheduled tasks, multi-company support, and customizable data filters, 
            this connector eliminates manual data handling and ensures BigQuery always reflects the latest Odoo updates.  
            Perfect for teams seeking accurate insights, automated data pipelines, and powerful reporting capabilities.
        </p>
        <h2>Key Features</h2>
        <ul>
            <li>Two-way Odoo ↔ BigQuery data synchronization</li>
            <li>Real-time data sync for live analytics and dashboards</li>
            <li>Automated data export/import with scheduled operations</li>
            <li>Partial field sync for selective data transfer</li>
            <li>Dynamic BigQuery table selection and flexible mapping</li>
            <li>Advanced filtering with domains, conditions, and custom queries</li>
            <li>Multi-company support with independent data configurations</li>
            <li>Smart availability checks before every data transfer</li>
            <li>Comprehensive logging recorded directly in BigQuery</li>
            <li>User-friendly setup with no technical expertise required</li>
        </ul>
        <h2>Benefits</h2>
        <ul>
            <li>Centralizes analytics by bringing Odoo data into BigQuery for powerful BI insights</li>
            <li>Enables accurate, real-time visibility across Sales, Finance, Inventory & CRM</li>
            <li>Eliminates repetitive manual exports, scripts, and spreadsheet handling</li>
            <li>Boosts decision-making with up-to-date dashboards and predictive analysis</li>
            <li>Supports large datasets and high-volume Odoo environments</li>
            <li>Keeps systems synchronized effortlessly through automated workflows</li>
        </ul>
        <h2>Why Choose This Odoo BigQuery Connector?</h2>
        <p>
            This connector delivers a robust, scalable, and automation-driven integration between Odoo and Google BigQuery. 
            It empowers organizations to harness real-time business intelligence, unify multi-company data, 
            and build modern, AI-ready analytics pipelines without coding. Designed for both small and large enterprises, 
            it provides a reliable and intuitive solution for high-performance reporting and seamless Odoo–BigQuery connectivity.
        </p>
        <h2>SEO Keywords</h2>
        <p>
            Odoo BigQuery Connector, Odoo BigQuery Integration, Google BigQuery Odoo Connector, 
            Odoo Data Export to BigQuery, BigQuery Odoo Sync, Odoo BI Analytics, Real-Time BigQuery Odoo Sync, 
            Odoo to BigQuery Import Export, Odoo Data Pipeline, Odoo BigQuery Reporting
        </p>
        <h2>Related Apps</h2>
        <ul>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_tableau_desktop_connector">Tableau Desktop Connector</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_tableau_desktop_connector_with_sql">Tableau Desktop Connector With SQL</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_tiktok_shop_connector">TikTok Shop Connector</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_recurly_connector">Recurly Subscription Connector</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_smartsheet_connector">Smartsheet Connector</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_power_bi_desktop_connector">Odoo PowerBi Connector</a></li>
        </ul>
        <p>For custom Odoo integrations, visit <a href="https://creyox.com">creyox.com</a></p>
        <p>Watch the YouTube demo: <a href="https://youtu.be/w9e8E7tU_NM">Odoo BigQuery Connector Demo</a></p>
        <p>Read our blog: <a href="https://www.creyox.com/blog/seamlessly-integrate-odoo-with-bigquery-for-powerful-data-analytics-20/seamlessly-integrate-odoo-with-bigquery-for-powerful-data-analytics-18">Odoo BigQuery Connector Guide</a></p>
        """,
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/bigquery_config_views.xml",
        "views/bigquery_export_views.xml",
        "views/bigquery_scheduler_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
    "price": 425,
    "currency": "USD",
}
