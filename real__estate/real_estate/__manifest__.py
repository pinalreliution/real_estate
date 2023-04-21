# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Real Estate ',
    'version': '1.0.1',
    'category': 'Real Estate/Brokerage',
    'summary': '',
    'description': """ """,
    'depends': ['sale', 'base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/real_estate_security.xml',

        'views/real_estate_properties.xml',
        'views/real_estate_property_types.xml',
        'views/real_estate_property_tags.xml',
        'views/real_estate_property_offers.xml',
        'views/inherit_res_users.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_real_estate_config_setting.xml',
        'views/server_action.xml',

        'report/real_estate_offers_reports.xml',
        'report/real_estate_offers_template.xml',
        'report/real_estate_salesman_template.xml',

        'data/ir_sequence_data.xml',
        'data/schedule_action.xml',
        'data/email_template.xml',
        'data/real_estate_data.xml',

        'wizard/create_token_wizard_view.xml',
    ],
    'demo': [],
    'application': True,
    'sequence': -100,
    'installable': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
