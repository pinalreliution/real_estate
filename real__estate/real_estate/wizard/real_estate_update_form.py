# -*- coding: utf-8 -*-

from odoo import api, fields, models


class UpdateFormWizard(models.TransientModel):
    _name = 'create.token.wizard'
    # _name = 'update.form.wizard'
    _description = 'Create Token Wizard'

    name = fields.Char(string='Property Type')
    garden_area = fields.Integer(string='Garden Area')
    # property_type_id = fields.Many2one(comodel_name='property.types', string='Property Type')
    # salesman_id = fields.Many2one(comodel_name='res.users', string='Salesperson', default=lambda self: self.env.user)
    # buyer_id = fields.Many2one(comodel_name='res.partner', string='Buyer')
    # postcode = fields.Char(string='Postcode', required=True, tracking=True)


    def action_update_button(self):
        print("click button...")
        self.env['real.estate'].browse(self._context.get("active_ids")).update({'garden_area': self.garden_area})
        return True

        # How To Create Record From Code In Odoo
        # vals = {
        #     'name': self.name
        # }
        # self.env['real.estate'].create(vals)