# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
from requests.auth import HTTPBasicAuth


class ResCompany(models.Model):
    _inherit = "res.company"

    chargebee_id = fields.Char(string="Chargebee ID", index=True)
    def get_or_create_company_from_chargebee(self, cb_be_id=False):
        """
        If cb_be_id provided:
            → Fetch specific BE from Chargebee and create/update company.
        If cb_be_id not provided:
            → Fetch ALL Business Entities from Chargebee and create companies.
        """
        # Load Chargebee config
        config = self.env['chargebee.configuration'].search([], limit=1)
        if not config or not config.api_key or not config.site_name:
            raise UserError(_("Chargebee configuration missing."))

        api_key = config.api_key
        site = config.site_name

        if cb_be_id:
            existing = self.search([('chargebee_id', '=', cb_be_id)], limit=1)
            if existing:
                return existing
            url = f"https://{site}.chargebee.com/api/v2/business_entities/{cb_be_id}"
            response = requests.get(url, auth=HTTPBasicAuth(api_key, ""))
            if response.status_code != 200:
                raise UserError(_(
                    f"Failed to retrieve Business Entity {cb_be_id}: {response.text}"
                ))
            be_data = response.json().get("business_entity")
            return self._create_company_from_be(be_data)

        # if no be id provided sync all companies
        url = f"https://{site}.chargebee.com/api/v2/business_entities"

        response = requests.get(url, auth=HTTPBasicAuth(api_key, ""))
        if response.status_code != 200:
            raise UserError(_(
                f"Failed to retrieve Business Entities: {response.text}"
            ))
        companies = []
        be_list = response.json().get("list", [])
        for be_wrapper in be_list:
            be = be_wrapper.get("business_entity")
            if not be:
                continue

            cb_id = be.get("id")
            existing = self.search([('chargebee_id', '=', cb_id)], limit=1)
            if existing:
                companies.append(existing)
            else:
                companies.append(self._create_company_from_be(be))

        return companies

    def _create_company_from_be(self, be_data):
        """Internal method to create Odoo company from Chargebee BE object."""
        cb_id = be_data.get("id")
        be_name = be_data.get("name") or f"Chargebee - {cb_id}"
        be_currency = be_data.get("currency_code") or "USD"
        currency = self.env['res.currency'].search(
            [('name', '=', be_currency), ('active', 'in', [True, False])],
            limit=1
        )
        if not currency:
            currency = self.env['res.currency'].create({
                'name': be_currency,
                'symbol': be_currency,
                'active': True,
            })

        return self.create({
            'name': be_name,
            'currency_id': currency.id,
            'chargebee_id': cb_id,
        })
