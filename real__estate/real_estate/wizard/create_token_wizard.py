# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CreateTokenWizard(models.TransientModel):
    _name = 'create.token.wizard'
    _description = 'Create Token Wizard'

    name = fields.Char(string='Property Type')
    # property_type_id = fields.Many2one(comodel_name='property.types', string='Property Type')
    # salesman_id = fields.Many2one(comodel_name='res.users', string='Salesperson', default=lambda self: self.env.user)
    # buyer_id = fields.Many2one(comodel_name='res.partner', string='Buyer')
    # postcode = fields.Char(string='Postcode', required=True, tracking=True)

    # How To Create Record From Code In Odoo
    def action_create_button(self):
        print("click button...")
        vals = {
            'name': self.name
        }
        self.env['real.estate'].create(vals)