# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class InheritResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(comodel_name='real.estate', inverse_name='salesman_id',
                                   domain="[('state','in', ['new','offer_received'])]")
    # email = fields.Char(string='Email')


# Inherit and add New Value To Selection Field Odoo
class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(selection_add=[('real_estate', 'Real Estate')])