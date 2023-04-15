# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CreateTokenWizard(models.TransientModel):
    _name = 'create.token.wizard'
    _description = 'Create Token Wizard'

    name = fields.Char(string='Person Name')


