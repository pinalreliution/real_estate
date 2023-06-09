# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from itertools import groupby
import json

import action as action
from lib2to3.fixes.fix_input import context

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils
import pytz


class RealEstate(models.Model):
    _name = "real.estate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Real Estate"
    _order = 'property_type_id desc'
    _rec_name = 'ref'

    pro_seq = fields.Char(string='Number', readonly=True)
    ref = fields.Char(string='Reference')
    name = fields.Char(string='Property Type', copy=False, required=True, readonly=False, default=lambda self: _('New'))
    description = fields.Text(string='Description', required=False)
    postcode = fields.Char(string='Postcode', required=True)
    date_availability = fields.Date(string='Available Form', copy=False, default=lambda self: fields.Date.today())
    user_time_zone = fields.Datetime(string='Date Time')
    expected_price = fields.Float(string='Expected Price', required=True, default=lambda self: _(2))
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
    cancel_date = fields.Date(string='Cancellation date')
    note = fields.Html(string='Note')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')

    # _sql_constraints = [
    #     ('check_expected_price', 'CHECK(expected_price > 0)',
    #      'A property expected price must be strictly positive'),
    #     ('check_selling_price', 'CHECK(selling_price > 0)',
    #      'A property selling price must be strictly positive')
    # ]

    # Onchange domain
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for offer in self:
            return {'domain': {'order_id': [('partner_id', '=', offer.partner_id.id)]}}

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

    def action_reset(self):
        for record4 in self:
            print(record4)
            if record4.state == 'canceled':
                return record4.env.ref('real_estate.real_estate_sever_action')

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

    def action_wizard_button(self):
        # Other type of call
        # return self.env['ir.actions.act_window']._for_xml_id("real_estate.action_update_form")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.token.wizard',
            'view_mode': 'form',
            'target': 'new'
        }

    # Schedule Action button
    def test_schedule(self):
        schedule = self.search([])
        for rec in schedule:
            if rec.state == 'new' and fields.Date.today() == rec.cancel_date:
                rec.write({'state': 'canceled'})

        # Other method
        # schedule = self.search([('|', ('state', '=', 'new'), ('cancel_date', '=', 'fields.Date.today()'))])
        # for rec in schedule:
        #     rec.write({'state': 'canceled'})

    @api.model
    def default_get(self, fields):
        vals = super(RealEstate, self).default_get(fields)
        vals['cancel_date'] = datetime.now() + timedelta(days=5)
        return vals

    # User Time Zone Button
    def action_user_time_zone(self):
        tz = pytz.timezone(self.env.user.partner_id.tz)
        utc_time = datetime.now()
        print("Utc time:", utc_time)
        tz_time = datetime.now(tz=tz)
        print("Local Time:", tz_time)

# Server Action
    def action_estate(self):
        print("Heyyyy....")
        return {
            'name': 'Real Estate Server Action',
            'view_type': 'form',
            'res_model': 'real.estate',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
        }

    # Mail button action
    # if Immediate mail send then used force_send attribute and in this time email status is delivering
    def action_send_email(self):
        # template = self.env.ref('real_estate.email_template_real_estate')
        # for rec1 in self:
        #     if rec1.buyer_id.email:
        #         template.send_mail(rec1.id, force_send=True)
        ctx = {
            'default_model': 'real.estate',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    # def action_wizard_button_with_context(self):
    #     actions = self.env["ir.actions.act_window"]._for_xml_id("real_estate.action_wizard_button_with_context")
    #     context = {
    #         'default_name': self.name,
    #         'default_expected_price': self.expected_price,
    #         'default_selling_price': self.selling_price,
    #     }
    #     actions['context'] = context
    #     return actions
