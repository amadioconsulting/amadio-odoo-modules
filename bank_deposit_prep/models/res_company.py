# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    deposit_bank_institution = fields.Char(
        string='Bank Institution Number',
        help='3-digit institution (bank) number for deposit slips.',
    )
    deposit_bank_transit = fields.Char(
        string='Branch Transit Number',
        help='5-digit branch transit number for deposit slips.',
    )
    deposit_bank_account = fields.Char(
        string='Bank Account Number',
        help='Account number shown on deposit slips.',
    )
    deposit_bank_name = fields.Char(
        string='Bank Name',
        help='Name of the bank displayed on the deposit slip header.',
    )
    deposit_slip_footer = fields.Char(
        string='Deposit Slip Footer Note',
        help='Optional note printed at the bottom of each deposit slip.',
    )
