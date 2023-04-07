# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# from datetime import datetime, timedelta

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils


class PropertyOffers(models.Model):
    _name = "property.offers"
    _description = "Property Offers"
    _order = 'price desc'

    price = fields.Float(string='Price')
    status = fields.Selection(string='Status', copy=False, selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    property_id = fields.Many2one(comodel_name='real.estate', string='Property', required=True)
    validity = fields.Integer(string='Validity(days)', default=lambda self: _(7))
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse="_inverse_date_deadline",
                                default=fields.datetime.now(), string='Deadline', store=True)
    property_type_id = fields.Many2one(comodel_name='property.types', related='property_id.property_type_id')
    # create_date = fields.Date(string='Create Date')

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for rec in self:
            if rec.create_date:
                rec.date_deadline = rec.create_date.date() + timedelta(days=rec.validity)
            else:
                fields.Date.today()

    @api.depends("create_date", "date_deadline")
    def _inverse_date_deadline(self):
        for rec1 in self:
            if rec1.create_date:
                var = rec1.create_date.date()
                rec1.validity = (rec1.date_deadline - var).days
            else:
                fields.Date.today()

    def action_accept(self):
        for rec2 in self:
            rec2.write({'status': 'accepted'})
            rec2.property_id.write({
                'state': 'offer_accepted',
                'selling_price': rec2.price,
                'buyer_id': rec2.partner_id
            })

    def action_refuse(self):
        for rec3 in self:
            rec3.write({'status': 'refused'})

    @api.model
    def write(self, vals):
        rec5 = super().write(vals)
        for rec4 in self:
            rec4.property_id.state = 'offer_received'
            if rec4.property_id.best_price > rec4.price:
                raise UserError(_("The offer must be higher than best price.."))
        return rec5

    @api.model
    def create(self, vals):
        self.env['real.estate'].browse(vals['property_id'])
        return super(PropertyOffers, self).create(vals)
