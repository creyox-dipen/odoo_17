# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    'name': 'smart payment term recommender | payment term prediction | invoice based term suggestion | customer credit analysis | dynamic payment term | odoo payment term module | invoice scoring system | smart invoice terms | automatic term assignment | kpi based term mapping | customer scoring',
    'author': 'Creyox Technologies',
    "website": "https://www.creyox.com",
    'support': 'support@creyox.com',
    'category': 'accounting',
    'summary': """
    The Smart Payment Term Recommender module enhances invoicing efficiency in Odoo by intelligently recommending the most suitable payment terms for customers based on their past invoice behavior and financial history. This tool automates the process of evaluating customer payment performance using predefined scoring rules and KPI-based matrices, helping businesses make informed decisions and reduce credit risks.
    
    When a user selects a customer while creating a new invoice, the module automatically analyzes the customer's historical data—such as average payment days, overdue invoice count, and refund ratios—against a configurable scoring matrix. Based on the final calculated score, the system suggests the most appropriate payment term, improving billing accuracy and customer-specific credit management. For new customers with no prior invoice history, the module displays a custom message, while unmatched score scenarios are clearly flagged to the user.
    
    The module allows users to configure flexible KPI rules, assign weightages, and define score ranges linked to various payment terms. Admins can also manage these configurations from the Invoicing menu under Payment Matrix Configuration. With automated scoring and term mapping, the Smart Payment Term Recommender eliminates guesswork, ensures consistency, and enhances customer trust through transparent and data-backed term allocation.
    
    smart payment term recommender,
    customer payment term prediction,
    invoice scoring odoo,
    automatic payment term selection,
    payment term matrix odoo,
    payment score system,
    odoo payment behavior analysis,
    odoo invoice term automation,
    credit evaluation odoo,
    customer financial history odoo,
    odoo customer risk profiling,
    overdue invoice analysis,
    refund ratio scoring,
    odoo scoring engine,
    payment term recommendation system,
    odoo invoice automation,
    odoo payment analytics,
    odoo credit term decision engine,
    auto select payment terms odoo,
    payment term mapping rules,
    odoo financial kpi scoring,
    smart invoicing odoo,
    customer term intelligence,
    odoo customer scoring module,
    payment rules engine odoo,
    odoo predictive payment term,
    data-driven term suggestion odoo,
    """,
    "license": "OPL-1",
    "version": "17.0",
    'description': """
    The Smart Payment Term Recommender module enhances invoicing efficiency in Odoo by intelligently recommending the most suitable payment terms for customers based on their past invoice behavior and financial history. This tool automates the process of evaluating customer payment performance using predefined scoring rules and KPI-based matrices, helping businesses make informed decisions and reduce credit risks.
    
    When a user selects a customer while creating a new invoice, the module automatically analyzes the customer's historical data—such as average payment days, overdue invoice count, and refund ratios—against a configurable scoring matrix. Based on the final calculated score, the system suggests the most appropriate payment term, improving billing accuracy and customer-specific credit management. For new customers with no prior invoice history, the module displays a custom message, while unmatched score scenarios are clearly flagged to the user.
    
    The module allows users to configure flexible KPI rules, assign weightages, and define score ranges linked to various payment terms. Admins can also manage these configurations from the Invoicing menu under Payment Matrix Configuration. With automated scoring and term mapping, the Smart Payment Term Recommender eliminates guesswork, ensures consistency, and enhances customer trust through transparent and data-backed term allocation.
    
    smart payment term recommender,
    customer payment term prediction,
    invoice scoring odoo,
    automatic payment term selection,
    payment term matrix odoo,
    payment score system,
    odoo payment behavior analysis,
    odoo invoice term automation,
    credit evaluation odoo,
    customer financial history odoo,
    odoo customer risk profiling,
    overdue invoice analysis,
    refund ratio scoring,
    odoo scoring engine,
    payment term recommendation system,
    odoo invoice automation,
    odoo payment analytics,
    odoo credit term decision engine,
    auto select payment terms odoo,
    payment term mapping rules,
    odoo financial kpi scoring,
    smart invoicing odoo,
    customer term intelligence,
    odoo customer scoring module,
    payment rules engine odoo,
    odoo predictive payment term,
    data-driven term suggestion odoo,
    """,

    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_term_matrix.xml',
        'views/payment_term_matrix_rule.xml',
        'views/payment_term_matrix_rule_line.xml',
        'views/payment_term_mapping_rule.xml',
        'data/payment_term_matrix_data.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    "price": 80,
    'currency': 'USD'
}
