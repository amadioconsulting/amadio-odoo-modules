# -*- coding: utf-8 -*-
{
    'name': 'Household & Family Contact Management',
    'version': '18.0.1.0.2',
    'category': 'Sales/CRM',
    'summary': (
        'Model households as a single contact with multiple members, '
        'auto-generate "Mr. & Mrs. Smith" combined salutations, and group '
        'family communications — without duplicating addresses.'
    ),
    'description': """
Household & Family Contact Management
======================================

Odoo's standard contact model is built for businesses, not families. This module
adds a lightweight but powerful Household layer — perfect for churches, nonprofits,
schools, membership organizations, clubs, and any CRM tracking family units.

Key Features
------------
* **Household records** — A dedicated contact type that groups family members under one address
* **Auto-generated salutations** — "Mr. & Mrs. Smith", "The Johnson Family", or fully custom
* **Member roles** — Primary contact, spouse/partner, child, dependent, and other
* **Address inheritance** — Members inherit the household address unless overridden
* **Smart search** — Find any household by any member's name
* **Combined mailing** — Email blast to household goes to the primary contact, or to all adults
* **Donation-ready** — Households can be used as donation sources; combined giving tracked at household level
* **CRM integration** — Link opportunities, donations, and activities to the household OR individual members
* **Anniversary & birthday tracking** — Store wedding anniversary and member birthdays

Who Uses This
-------------
* Churches & religious organizations (parish families, couples, families)
* Nonprofits and charities (donor family records)
* Private schools & tutoring (family billing contact)
* Clubs & membership organizations (family memberships)
* Estate planning, legal, and financial advisors (household wealth management)

Compatibility
-------------
* Odoo 18.0
* Extends standard res.partner — no data migration required
* Compatible with all existing contacts
    """,
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'depends': ['contacts', 'mail'],
    "data": [
        "security/ir.model.access.csv",
        "views/household_views.xml",
        "views/res_partner_views.xml",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 59.00,
    'currency': 'EUR',
}
