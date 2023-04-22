# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    postcode = fields.Char(string='Postcode')
    # policy = fields.Char(string='Policy')


class InheritResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    # policy = fields.Char(string='Policy')
    policy = fields.Html(string='Custom Policy')

    def set_values(self):
        rec = super(InheritResConfig, self).set_values()
        print('rec', rec)
        self.env['ir.config_parameter'].set_param('real_estate.policy', self.policy)
        return rec

    @api.model
    def get_values(self):
        res = super(InheritResConfig, self).get_values()
        print('res', res)
        ICPSudo = self.env['ir.config_parameter']
        print('vals', ICPSudo)
        polices = ICPSudo.get_param('real_estate.policy')
        print('policy', polices)
        res.update(
            policy=polices
        )
        return res