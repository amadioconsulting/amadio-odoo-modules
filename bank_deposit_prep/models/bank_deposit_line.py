# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BankDepositLine(models.Model):
    _name = 'bank.deposit.line'
    _description = 'Bank Deposit Line'
    _order = 'payment_type, sequence, id'

    deposit_id = fields.Many2one(
        'bank.deposit',
        string='Deposit',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        ondelete='restrict',
        domain=[('state', '=', 'posted')],
    )
    payer_name = fields.Char(
        string='Payer / Description',
        required=True,
    )
    payment_type = fields.Selection([
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('eft', 'EFT / Wire'),
        ('other', 'Other'),
    ], string='Type', required=True, default='cheque')
    cheque_number = fields.Char(string='Cheque #')
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='deposit_id.currency_id',
        store=True,
    )
    notes = fields.Char(string='Notes')

    @api.onchange('payment_id')
    def _onchange_payment_id(self):
        if self.payment_id:
            pay = self.payment_id
            self.payer_name = pay.partner_id.name or pay.name or ''
            self.amount = pay.amount
            # Auto-detect payment type from journal
            journal = pay.journal_id
            if journal.type == 'cash':
                self.payment_type = 'cash'
            elif pay.payment_method_line_id and 'check' in (pay.payment_method_line_id.name or '').lower():
                self.payment_type = 'cheque'
            else:
                self.payment_type = 'cheque'

    @api.constrains('payment_id', 'deposit_id')
    def _check_payment_not_duplicate(self):
        for line in self:
            if not line.payment_id:
                continue
            duplicate = self.search([
                ('payment_id', '=', line.payment_id.id),
                ('deposit_id.state', '=', 'confirmed'),
                ('deposit_id', '!=', line.deposit_id.id),
                ('id', '!=', line.id),
            ])
            if duplicate:
                raise ValidationError(_(
                    'Payment "%s" is already included in confirmed deposit %s.',
                    line.payment_id.name,
                    duplicate[0].deposit_id.name,
                ))
