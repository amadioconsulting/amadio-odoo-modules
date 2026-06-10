# -*- coding: utf-8 -*-
{
    'name': 'Bank Deposit Preparation & Slip Generator',
    'version': '18.0.1.0.2',
    'category': 'Accounting/Accounting',
    'summary': (
        'Group payments into bank deposit batches, generate printable deposit slips, '
        'and track deposit status from preparation through bank confirmation.'
    ),
    'description': """
Bank Deposit Preparation & Slip Generator
==========================================

Stop manually tallying deposits on paper. This module lets you batch payments
into formal deposit records, automatically totals cheques, cash, and EFTs, and
produces a clean, printable deposit slip PDF — ready to hand to your bank teller
or attach to your accounting records.

Key Features
------------
* **Flexible batching** — add any posted payment to a deposit batch; one click selects all outstanding items
* **Auto-classification** — payments are automatically sorted into Cheque, Cash, EFT/Wire, and Credit Card columns
* **Configurable bank info** — institution code, transit number, and account number stored per company; no hardcoding
* **Sequential deposit numbers** — automatic DEP/YYYY/##### reference numbering
* **Professional PDF slip** — bank-ready layout with date, deposit total, breakdown by type, individual line items, and preparator signature line
* **Status workflow** — Draft → Prepared → Deposited → Confirmed; mark confirmed with bank reference number
* **Duplicate safeguard** — payments already on a confirmed deposit cannot be added again

Who Uses This
-------------
Churches, nonprofits, schools, retail businesses, and professional offices — any organization that
makes regular bank deposits and needs a paper/PDF trail.

Compatibility
-------------
* Odoo 18.0
* Works with multi-company and multi-currency configurations
* Compatible with any chart of accounts
    """,
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'depends': ['account', 'mail'],
    "data": [
        "security/ir.model.access.csv",
        "data/deposit_sequence.xml",
        "views/bank_deposit_views.xml",
        "views/res_config_settings_views.xml",
        "report/deposit_slip_report.xml",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 69.00,
    'currency': 'EUR',
}
