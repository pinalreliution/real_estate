# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Real Estate Account ',
    'version': '1.0.1',
    'category': '',
    'summary': '',
    'description': """ """,
    'depends': ['real_estate', 'account'],
    'data': [
        'report/inherit_real_estate_account_template.xml',
        'report/real_estate_account_report.xml'
    ],
    'demo': [],
    'application': True,
    'sequence': -100,
    'installable': True,
    'auto_install': False,
    'assets': {},
    'license': 'LGPL-3',
}
