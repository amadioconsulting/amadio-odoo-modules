# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deposit_bank_institution = fields.Char(
        related='company_id.deposit_bank_institution',
        readonly=False,
        string='Bank Institution Number',
    )
    deposit_bank_transit = fields.Char(
        related='company_id.deposit_bank_transit',
        readonly=False,
        string='Branch Transit Number',
    )
    deposit_bank_account = fields.Char(
        related='company_id.deposit_bank_account',
        readonly=False,
        string='Bank Account Number',
    )
    deposit_bank_name = fields.Char(
        related='company_id.deposit_bank_name',
        readonly=False,
        string='Bank Name',
    )
    deposit_slip_footer = fields.Char(
        related='company_id.deposit_slip_footer',
        readonly=False,
        string='Deposit Slip Footer Note',
    )
