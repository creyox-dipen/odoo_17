# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import models, fields, api, _

ACCOUNT_DOMAIN = "['&', '&', ('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card','off_balance')), ('company_id', '=', current_company_id)]"


class UpdateProductAccount(models.TransientModel):
    _name = 'update.product.accounts'
    _description = 'Update Product Accounts'

    change_type = fields.Selection([('category', 'Product Category wise'),
                                    ('product', 'Product wise')], default='category',
                                   string='Change Product Tax')
    change_account_type = fields.Selection(
        [('income', 'Income Account'), ('expense', 'Expense Account'), ('both', 'Both')],
        default='income', string='Change which account of product')
    income_account_id = fields.Many2one('account.account',
                                        help="Set the Income account of product.", string='Income Account',
                                        domain=ACCOUNT_DOMAIN, company_dependent=True)
    expense_account_id = fields.Many2one('account.account',
                                         help="Set the Expense account of product.", string='Income Account',
                                         domain=ACCOUNT_DOMAIN, company_dependent=True)
    categ_id = fields.Many2one('product.category', string='Product Category')
    product_id = fields.Many2many('product.product', 'rel_product_account_update', string='Product')

    def update_product_account(self):
        if self.change_type == 'category':
            products = self.env['product.product'].search([('categ_id', '=', self.categ_id.id)])
            if self.change_account_type == 'income':
                for rec in products:
                    rec.property_account_income_id = self.income_account_id.id
            elif self.change_account_type == 'expense':
                for rec in products:
                    rec.property_account_expense_id = self.expense_account_id.id
            else:
                for rec in products:
                    rec.property_account_income_id = self.income_account_id.id
                    rec.property_account_expense_id = self.expense_account_id.id

        elif self.change_type == 'product':
            products = self.env['product.product'].search([('id', 'in', self.product_id.ids)])
            if self.change_account_type == 'income':
                for rec in products:
                    rec.property_account_income_id = self.income_account_id.id
            elif self.change_account_type == 'expense':
                for rec in products:
                    rec.property_account_expense_id = self.expense_account_id.id
            else:
                for rec in products:
                    rec.property_account_income_id = self.income_account_id.id
                    rec.property_account_expense_id = self.expense_account_id.id
