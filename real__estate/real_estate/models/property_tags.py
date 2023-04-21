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


class PropertyTags(models.Model):
    _name = "property.tags"
    _description = "Property Tags"
    _order = 'name'

    name = fields.Char(string='Tags', required=True)
    color = fields.Integer(string='Color')
    color_2 = fields.Char(string='Color 2')

    # _sql_constrains = [
    #     ('name_unique', 'unique(name)', 'A property tag name must be unique.')
    # ]

    @api.constrains('name')
    def _check_name(self):
        for tag in self:
            if tag.name:
                raise ValidationError("A Property Tag name must be unique.")
