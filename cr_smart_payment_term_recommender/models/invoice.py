# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = ["account.move"]

    @api.onchange("partner_id")
    def calculate_customer_invoice_score(self):
        if len(list(self.partner_id)):
            customer_invoices = self.env["account.move"].search(
                [
                    ("partner_id", "=", self.partner_id.id),
                    ("state", "=", "posted"),
                    ("move_type", "=", "out_invoice"),
                ]
            )
            if len(list(customer_invoices)) == 0:
                self.payment_term_recommendation_notification("no_records")
                return
            payment_matrices = self.env["payment.term.matrix.rule"].search([])
            kpi_scores = []
            for matrix in payment_matrices:
                match matrix.matrix_id.id:
                    case 1:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.cal_avg_days_to_pay(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 2:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.on_time_percent(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 3:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.overdue_invoice_count(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 4:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.oldest_overdue_age(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 5:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.order_frequency_monthly(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 6:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.sales_volume_6mo(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 7:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.outstanding_balance(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 8:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.credit_note_ratio(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 9:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.days_since_last_payment(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 10:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.first_sale_age(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 11:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.avg_order_value(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 12:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.dispute_count(customer_invoices, rules)
                        kpi_scores.append(score)
                    case 13:
                        rules = self.env["payment.term.matrix.rule.line"].search(
                            [("rule_id", "=", matrix.id)]
                        )
                        score = self.invoice_volume_monthly(customer_invoices, rules)
                        kpi_scores.append(score)

            mapping_rules = self.env["payment.term.mapping.rule"].search([])
            result_payment_term = None
            total_score = sum(kpi_scores)
            for mapping_rule in mapping_rules:
                if (
                    total_score >= mapping_rule.score_min
                    and total_score <= mapping_rule.score_max
                ):
                    result_payment_term = mapping_rule.payment_term_id.name
            self.payment_term_recommendation_notification(result_payment_term)

    def payment_term_recommendation_notification(self, payment_term):
        if payment_term == "no_records":
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "type": "info",
                    "title": "New Customer",
                    "message": f"This Customer Has No Invoice Records",
                },
            )

        elif payment_term:
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "type": "success",
                    "title": "Recommended Payment Term",
                    "message": f"{payment_term} is Recommended",
                },
            )
        else:
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "type": "warning",
                    "title": "Payment Term !!",
                    "message": "No Payment Term Matched To This Customer Score",
                },
            )

    def find_invoice_payment_date(self, invoice):
        if invoice:
            payment_dates = []
            invoice_name = invoice.payment_reference
            payment_recs = self.env["account.payment"].search(
                [("ref", "=", invoice_name)]
            )
            for rec in payment_recs:
                payment_dates.append(rec.date)
            return max(payment_dates)

    def verify_rules(self, rules, value):
        """
        Generate the score based on the user defined rules
        """
        for rule in rules:
            if rule.operator == "lt":
                if value < rule.value_1:
                    return rule.score
            elif rule.operator == "le":
                if value <= rule.value_1:
                    return rule.score
            elif rule.operator == "gt":
                if value > rule.value_1:
                    return rule.score
            elif rule.operator == "ge":
                if value >= rule.value_1:
                    return rule.score
            elif rule.operator == "eq":
                if value == rule.value_1:
                    return rule.score
            else:
                if value >= rule.value_1 and value <= rule.value_2:
                    return rule.score

    def cal_avg_days_to_pay(self, invoices, rules):
        """
        This method calculates the customer payment score based on average score of each invoice's score
        """
        per_invoice_score = []
        total_paid_invoices = 0
        for invoice in invoices:
            if invoice.payment_state == "paid":
                total_paid_invoices += 1
                invoice_confirm_date = invoice.invoice_date
                payment_date = self.find_invoice_payment_date(invoice)
                days_to_pay = (payment_date - invoice_confirm_date).days
                per_invoice_score.append(self.verify_rules(rules, days_to_pay))
        try:
            total_score = sum(per_invoice_score) / total_paid_invoices
            return total_score
        except ZeroDivisionError:
            return 0

    def on_time_percent(self, invoices, rules):
        """
        This method calculates the score based on percentage of payment done before due date.
        """
        total_paid_invoices = 0
        on_time_invoices = 0
        for invoice in invoices:
            if invoice.payment_state == "paid":
                total_paid_invoices += 1
                invoice_due_date = invoice.invoice_date_due
                payment_date = self.find_invoice_payment_date(invoice)
                if payment_date <= invoice_due_date:
                    on_time_invoices += 1
        try:
            ontime_invoice_percentage = (100 * on_time_invoices) / total_paid_invoices
            return (
                self.verify_rules(rules, ontime_invoice_percentage)
                if self.verify_rules(rules, ontime_invoice_percentage) != None
                else 0
            )
        except ZeroDivisionError:
            return 0

    def overdue_invoice_count(self, invoices, rules):
        """
        This method calculate customer score based on overdue invoice payments
        """
        overdue_invoices = 0
        for invoice in invoices:
            if invoice.payment_state == "paid":
                invoice_due_date = invoice.invoice_date_due
                payment_date = self.find_invoice_payment_date(invoice)
                if payment_date > invoice_due_date:
                    overdue_invoices += 1
        return (
            self.verify_rules(rules, overdue_invoices)
            if self.verify_rules(rules, overdue_invoices) != None
            else 0
        )

    def oldest_overdue_age(self, invoices, rules):
        """
        This method calculate customer score based the oldest overdue invoice payment
        """
        days = 0
        max_date = None
        for invoice in invoices:
            if invoice.payment_state == "paid":
                payment_date = self.find_invoice_payment_date(invoice)
                if payment_date > invoice.invoice_date_due:
                    max_date = payment_date
                    break
        for invoice in invoices:
            if invoice.payment_state == "paid":
                payment_date = self.find_invoice_payment_date(invoice)
                if payment_date > invoice.invoice_date_due:
                    if max_date <= payment_date:
                        max_date = payment_date
                        days = (payment_date - invoice.invoice_date_due).days
        return (
            self.verify_rules(rules, days)
            if self.verify_rules(rules, days) != None
            else 0
        )

    def order_frequency_monthly(self, invoices, rules):
        """
        This method calculates the customer score based on average confirmed orders for last 6 months
        """
        months = 6
        current_date = date.today()
        monthly_dates = [current_date - relativedelta(months=months)]
        while months:
            monthly_dates.append((monthly_dates[6 - months] + relativedelta(months=1)))
            months -= 1
        monthly_order_frequency = [0, 0, 0, 0, 0, 0]
        for invoice in invoices:
            if (
                invoice.invoice_date >= monthly_dates[0]
                and invoice.invoice_date <= monthly_dates[1]
            ):
                monthly_order_frequency[0] += 1
            elif (
                invoice.invoice_date > monthly_dates[1]
                and invoice.invoice_date <= monthly_dates[2]
            ):
                monthly_order_frequency[1] += 1
            elif (
                invoice.invoice_date > monthly_dates[2]
                and invoice.invoice_date <= monthly_dates[3]
            ):
                monthly_order_frequency[2] += 1
            elif (
                invoice.invoice_date > monthly_dates[3]
                and invoice.invoice_date <= monthly_dates[4]
            ):
                monthly_order_frequency[3] += 1
            elif (
                invoice.invoice_date > monthly_dates[4]
                and invoice.invoice_date <= monthly_dates[5]
            ):
                monthly_order_frequency[4] += 1
            else:
                monthly_order_frequency[5] += 1

        average_order_frequency = sum(monthly_order_frequency) / len(
            monthly_order_frequency
        )
        return (
            self.verify_rules(rules, average_order_frequency)
            if self.verify_rules(rules, average_order_frequency) != None
            else 0
        )

    def sales_volume_6mo(self, invoices, rules):
        """
        This method calculates the customer score based on amount of total confirmed sales in last 6 months
        """
        months = 6
        current_date = date.today()
        six_months_before_date = current_date - relativedelta(months=months)
        six_months_sales = 0
        for invoice in invoices:
            if (
                invoice.invoice_date >= six_months_before_date
                and invoice.invoice_date <= current_date
            ):
                six_months_sales += invoice.amount_total
        return (
            self.verify_rules(rules, six_months_sales)
            if self.verify_rules(rules, six_months_sales) != None
            else 0
        )

    def outstanding_balance(self, invoices, rules):
        """
        This method calculates the customer score based on Unpaid amount from all open invoices
        """
        outstanding_balance = 0
        for invoice in invoices:
            if invoice.payment_state == "not_paid":
                outstanding_balance += invoice.amount_residual
        return (
            self.verify_rules(rules, outstanding_balance)
            if self.verify_rules(rules, outstanding_balance) != None
            else 0
        )

    def credit_note_ratio(self, invoices, rules):
        """
        This method calculates the customer score based on the ratio of refund invoices to total invoices
        """
        reversed_invoices = 0
        for invoice in invoices:
            if invoice.payment_state == "reversed":
                reversed_invoices += 1
        reversed_invoices_percentage = (reversed_invoices * 100) / len(list(invoices))
        return (
            self.verify_rules(rules, reversed_invoices_percentage)
            if self.verify_rules(rules, reversed_invoices_percentage) != None
            else 0
        )

    def days_since_last_payment(self, invoices, rules):
        """
        This method calculates the customer score based on number of days since the last invoice paid
        """
        days = None
        flag = 0
        max_date = None
        for invoice in invoices:
            if invoice.payment_state == "paid":
                max_date = self.find_invoice_payment_date(invoice)
                break
        for invoice in invoices:
            if invoice.payment_state == "paid":
                payment_date = self.find_invoice_payment_date(invoice)
                flag = 1
                if max_date <= payment_date:
                    max_date = payment_date
                    days = (date.today() - payment_date).days
        if flag:
            return (
                self.verify_rules(rules, days)
                if self.verify_rules(rules, days) != None
                else 0
            )
        else:
            return 0

    def first_sale_age(self, invoices, rules):
        """
        This method calculates the customer score based on days since the first invoice
        """
        first_invoice_age = None
        min_date = None
        for invoice in invoices:
            min_date = invoice.invoice_date
            break
        for invoice in invoices:
            invoice_date = invoice.invoice_date
            if min_date >= invoice_date:
                min_date = invoice_date
                first_invoice_age = (date.today() - invoice_date).days
        return (
            self.verify_rules(rules, first_invoice_age)
            if self.verify_rules(rules, first_invoice_age) != None
            else 0
        )

    def avg_order_value(self, invoices, rules):
        """
        This method calculates the customer score based on average amount of order
        """
        per_invoice_amount = []
        for invoice in invoices:
            per_invoice_amount.append(invoice.amount_total)
        average_order_value = sum(per_invoice_amount) / len(list(invoices))
        return (
            self.verify_rules(rules, average_order_value)
            if self.verify_rules(rules, average_order_value) != None
            else 0
        )

    def dispute_count(self, invoices, rules):
        """
        This method calculates the customer score based on ratio of reversed orders to total orders
        """
        reversed_invoices = 0
        for invoice in invoices:
            if invoice.payment_state == "reversed":
                reversed_invoices += 1
        return (
            self.verify_rules(rules, reversed_invoices)
            if self.verify_rules(rules, reversed_invoices) != None
            else 0
        )

    def invoice_volume_monthly(self, invoices, rules):
        """
        This method calculates the customer score based on the number of invoices for past 6 months
        """
        months = 6
        current_date = date.today()
        monthly_dates = [current_date - relativedelta(months=months)]
        while months:
            monthly_dates.append((monthly_dates[6 - months] + relativedelta(months=1)))
            months -= 1
        monthly_invoices = [0, 0, 0, 0, 0, 0]
        for invoice in invoices:
            if (
                invoice.invoice_date >= monthly_dates[0]
                and invoice.invoice_date <= monthly_dates[1]
            ):
                monthly_invoices[0] += 1
            elif (
                invoice.invoice_date > monthly_dates[1]
                and invoice.invoice_date <= monthly_dates[2]
            ):
                monthly_invoices[1] += 1
            elif (
                invoice.invoice_date > monthly_dates[2]
                and invoice.invoice_date <= monthly_dates[3]
            ):
                monthly_invoices[2] += 1
            elif (
                invoice.invoice_date > monthly_dates[3]
                and invoice.invoice_date <= monthly_dates[4]
            ):
                monthly_invoices[3] += 1
            elif (
                invoice.invoice_date > monthly_dates[4]
                and invoice.invoice_date <= monthly_dates[5]
            ):
                monthly_invoices[4] += 1
            else:
                monthly_invoices[5] += 1

        average_monthly_invoices = sum(monthly_invoices) / len(list(monthly_invoices))
        return (
            self.verify_rules(rules, average_monthly_invoices)
            if self.verify_rules(rules, average_monthly_invoices) != None
            else 0
        )
