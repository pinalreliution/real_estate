# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils


class PropertyTypes(models.Model):
    _name = "property.types"
    _description = "Property Types"
    _order = 'name'

    name = fields.Char(string='Property Type', required=True)
    property_ids = fields.One2many(comodel_name='real.estate', inverse_name='property_type_id', string='Properties')
    sequence = fields.Integer(string='Sequence')
    offer_ids = fields.One2many(comodel_name='property.offers', inverse_name='property_type_id', string='Offers')
    offer_count = fields.Integer(compute="_compute_offer_ids", string='Offer Count')

    # _sql_constrains = [
    #     ('name_unique', 'unique(name)', 'A property type name must be unique.')
    # ]

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.name == self.name:
                raise ValidationError("A Property Type name must be unique.")

    @api.depends("offer_ids")
    def _compute_offer_ids(self):
        for record in self:
            record.offer_count = len(record.offer_ids)