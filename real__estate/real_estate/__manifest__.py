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
        'views/inherit_res_users.xml'
    ],
    'demo': [],
    'application': True,
    'sequence': -100,
    'installable': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
