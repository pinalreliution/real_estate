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


class RealEstate(models.Model):
    _name = "real.estate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Real Estate"
    _order = 'property_type_id desc'

    pro_seq = fields.Char(string='Number', readonly=True)
    name = fields.Char(string='Property Type', copy=False, required=True, readonly=False, default=lambda self: _('New'))
    description = fields.Text(string='Description', required=False)
    postcode = fields.Char(string='Postcode', required=True, tracking=True)
    date_availability = fields.Date(string='Available Form', copy=False, default=lambda self: fields.Date.today())
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', required=False, default=lambda self: _(2))
    living_area = fields.Integer(string='Living Area(sqr)', required=True)
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('west', 'West'),
        ('east', 'East')
    ])
    # Archive Field
    # active = fields.Boolean('Active')
    state = fields.Selection(string='Status', required=True, copy=False, selection=[
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], default=lambda self: _('new'))
    property_type_id = fields.Many2one(comodel_name='property.types', string='Property Type')
    salesman_id = fields.Many2one(comodel_name='res.users', string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one(comodel_name='res.partner', string='Buyer', copy=False)
    tag_ids = fields.Many2many(comodel_name='property.tags', string='Tags')
    offer_ids = fields.One2many(comodel_name="property.offers", inverse_name="property_id", string="Offers")
    total_area = fields.Float(compute="_compute_total_area", store=True, string='Total Area(sqr)')
    best_price = fields.Float(compute="_compute_offer_ids_price", store=True, string='Best Price')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)

    # _sql_constraints = [
    #     ('check_expected_price', 'CHECK(expected_price > 0)',
    #      'A property expected price must be strictly positive'),
    #     ('check_selling_price', 'CHECK(selling_price > 0)',
    #      'A property selling price must be strictly positive')
    # ]

    @api.onchange("garden")
    def _onchange_garden(self):
        for rec in self:
            if rec.garden:
                rec.garden_orientation = "north"
            else:
                rec.garden_orientation = None

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            if record.garden:
                record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_offer_ids_price(self):
        for offer in self:
            if offer.offer_ids:
                offer.best_price = max(offer.offer_ids.mapped('price'))

        # for record1 in self:
            # record1.best_price = 0
            # for offer1 in range(len(record1.offer_ids)):
            #     for offer2 in range(1 + offer1, len(record1.offer_ids)):
            #         if record1.offer_ids[offer1].price < record1.offer_ids[offer2].price:
            #             record1.best_price = record1.offer_ids[offer2].price

    def action_sold(self):
        for record2 in self:
            if 'canceled' in record2.state:
                raise UserError("Canceled Properties can not be sold.")
            return record2.write({'state': 'sold'})

    def action_cancel(self):
        for record3 in self:
            if 'sold' in record3.state:
                raise UserError("Sold Properties can not be canceled.")
            return record3.write({'state': 'canceled'})

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for price in self:
            if price.selling_price < 0.9 * price.expected_price:
                raise ValidationError(_("Selling price cannot be lower than 90% of the expected price."))

    @api.constrains('selling_price')
    def _check_price(self):
        for price1 in self:
            if price1.selling_price < 0 or price1.selling_price == 0:
                raise ValidationError(_("A property selling price must be strictly positive."))

    @api.constrains('expected_price')
    def _check_expected_price(self):
        for price2 in self:
            if price2.expected_price < 0 or price2.expected_price == 0:
                raise ValidationError(_("A property expected price must be strictly positive."))

    @api.constrains('best_price')
    def _check_best_price(self):
        for price3 in self:
            if price3.best_price < 0:
                raise ValidationError(_("A property best price must be strictly positive."))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_canceled(self):
        for record4 in self:
            if record4.state not in ['new', 'canceled']:
                raise UserError(_('Only new and canceled properties can be deleted.'))

    @api.model
    def create(self, vals):
        vals['pro_seq'] = self.env['ir.sequence'].next_by_code("real.estate")
        return super(RealEstate, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     rec = super(RealEstate, self).create(vals)
    #     vals['pro_seq'] = self.env['ir.sequence'].next_by_code("real.estate")
    #     return rec