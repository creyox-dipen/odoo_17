from odoo import models, fields


# wizard for generating report
class ProductWizard(models.TransientModel):
    _name = 'product.review.report.wizard'

    date1 = fields.Date(string='Start Date')
    date2 = fields.Date(string='Ending Date')
    min_rating = fields.Selection([('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)], string='Rating')
    approval_status = fields.Boolean(string='Approved Records')

    def generate_review_report(self):
        current_rec_id = self._context['current_product_template_id']

        product_record = self.env['product.product'].search([('product_tmpl_id', '=', int(current_rec_id))])

        reviews = self.env['product.review'].search([('product_id', '=', product_record.id)])
        value = ''''''
        filtered_reviews = []

        for review in reviews:
            if review:
                date1 = self.date1
                date2 = self.date2
                min_rating = int(self.min_rating)

                if self.approval_status == review.is_approved:
                    if review.review_date >= date1 and review.review_date <= date2:
                        if int(review.rating) >= min_rating:
                            filtered_reviews.append({
                                'review_customer': review.customer_id.name,
                                'review_rating': review.rating,
                                'review_comment': review.comment,
                            })

        print(value)
        datas = {
            'product_name': self._context['product_name'],
            'reviews': filtered_reviews
        }
        print(datas['product_name'])
        print(datas['reviews'])
        product_review_report_pdf = self.env.ref('cr_product_reviews.product_review_pdf_report_action_id',
                                                 raise_if_not_found=False)
        return product_review_report_pdf.report_action(self, data = datas)
