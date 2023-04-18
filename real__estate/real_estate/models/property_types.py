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

    ref = fields.Char(string='Reference', readonly=True)
    name = fields.Char(string='Property Type', required=True)
    property_ids = fields.One2many(comodel_name='real.estate', inverse_name='property_type_id', string='Properties')
    sequence = fields.Integer(string='Sequence')
    offer_ids = fields.One2many(comodel_name='property.offers', inverse_name='property_type_id', string='Offers')
    offer_count = fields.Integer(compute="_compute_offer_ids", string='Offer Count')
    active = fields.Boolean('Active')


    # _sql_constrains = [
    #     ('check_name', 'UNIQUE(name)', 'A property type name must be unique.')
    # ]


    @api.constrains('name')
    def _check_name(self):
        for types in self:
            if types.name == self.name:
                raise ValidationError("A Property Type name must be unique.")

    @api.depends("offer_ids")
    def _compute_offer_ids(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code("property.types")
        return super(PropertyTypes, self).create(vals)

    def name_get(self):
        property_list = []
        for rec1 in self:
            property_list.append((rec1.id, '[%s] %s' % (rec1.ref, rec1.name)))
        return property_list

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            record = self.search(['|', ('name', operator, name), ('ref', operator, name)])
            return record.name_get()
        return self.search([('name', operator, name)] + args, limit=limit).name_get()
        # return super(PropertyTypes, self).name_search(name=name, args=args, operator=operator, limit=limit)
