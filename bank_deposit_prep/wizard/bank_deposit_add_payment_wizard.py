# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class BankDepositAddPaymentWizard(models.TransientModel):
    _name = 'bank.deposit.add.payment.wizard'
    _description = 'Add Payments to Bank Deposit'

    deposit_id = fields.Many2one('bank.deposit', required=True, string='Deposit')
    journal_id = fields.Many2one('account.journal', string='Journal Filter')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To', default=fields.Date.context_today)
    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments to Add',
        domain="[('state', '=', 'posted'), ('payment_type', '=', 'inbound')]",
    )

    @api.onchange('journal_id', 'date_from', 'date_to')
    def _onchange_filters(self):
        """Suggest payments that are not yet on a confirmed deposit."""
        domain = [
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
        ]
        if self.journal_id:
            domain.append(('journal_id', '=', self.journal_id.id))
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        # Exclude payments already on a confirmed deposit
        confirmed_lines = self.env['bank.deposit.line'].search([
            ('deposit_id.state', '=', 'confirmed'),
            ('payment_id', '!=', False),
        ])
        already_deposited = confirmed_lines.mapped('payment_id').ids
        if already_deposited:
            domain.append(('id', 'not in', already_deposited))

        # Exclude payments already on the current deposit
        current_lines = self.env['bank.deposit.line'].search([
            ('deposit_id', '=', self.deposit_id.id),
            ('payment_id', '!=', False),
        ])
        current_payment_ids = current_lines.mapped('payment_id').ids
        if current_payment_ids:
            domain.append(('id', 'not in', current_payment_ids))

        self.payment_ids = self.env['account.payment'].search(domain)

    def action_add_to_deposit(self):
        """Create deposit lines for each selected payment."""
        deposit = self.deposit_id
        for pay in self.payment_ids:
            # Determine payment type
            if pay.journal_id.type == 'cash':
                ptype = 'cash'
            elif pay.payment_method_line_id and 'check' in (pay.payment_method_line_id.name or '').lower():
                ptype = 'cheque'
            else:
                ptype = 'cheque'

            self.env['bank.deposit.line'].create({
                'deposit_id': deposit.id,
                'payment_id': pay.id,
                'payer_name': pay.partner_id.name or pay.name or _('Unknown'),
                'amount': pay.amount,
                'payment_type': ptype,
            })
        return {'type': 'ir.actions.act_window_close'}
