# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BankDeposit(models.Model):
    _name = 'bank.deposit'
    _description = 'Bank Deposit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'

    name = fields.Char(
        string='Deposit Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    date = fields.Date(
        string='Deposit Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])],
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('deposited', 'Deposited'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft', tracking=True, copy=False)

    line_ids = fields.One2many(
        'bank.deposit.line',
        'deposit_id',
        string='Deposit Lines',
    )
    bank_reference = fields.Char(
        string='Bank Reference',
        help='Reference number provided by the bank upon confirmation.',
        tracking=True,
    )
    notes = fields.Text(string='Internal Notes')
    prepared_by_id = fields.Many2one(
        'res.users',
        string='Prepared By',
        default=lambda self: self.env.user,
        tracking=True,
    )
    confirmed_by_id = fields.Many2one(
        'res.users',
        string='Confirmed By',
        tracking=True,
    )
    confirmation_date = fields.Date(string='Confirmation Date', tracking=True)

    # Totals by type
    total_cheques = fields.Monetary(
        string='Total Cheques',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_cash = fields.Monetary(
        string='Total Cash',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_eft = fields.Monetary(
        string='Total EFT / Wire',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_other = fields.Monetary(
        string='Total Other',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_amount = fields.Monetary(
        string='Total Deposit',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    line_count = fields.Integer(
        string='# Items',
        compute='_compute_totals',
        store=True,
    )

    @api.depends('line_ids.amount', 'line_ids.payment_type')
    def _compute_totals(self):
        for rec in self:
            cheques = cash = eft = other = 0.0
            for line in rec.line_ids:
                if line.payment_type == 'cheque':
                    cheques += line.amount
                elif line.payment_type == 'cash':
                    cash += line.amount
                elif line.payment_type == 'eft':
                    eft += line.amount
                else:
                    other += line.amount
            rec.total_cheques = cheques
            rec.total_cash = cash
            rec.total_eft = eft
            rec.total_other = other
            rec.total_amount = cheques + cash + eft + other
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('bank.deposit') or _('New')
        return super().create(vals_list)

    def action_prepare(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Cannot prepare an empty deposit. Add at least one payment line.'))
            rec.state = 'prepared'

    def action_deposit(self):
        for rec in self:
            rec.state = 'deposited'

    def action_confirm(self):
        for rec in self:
            rec.confirmed_by_id = self.env.user
            rec.confirmation_date = fields.Date.today()
            rec.state = 'confirmed'

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise UserError(_('Confirmed deposits cannot be reset to draft.'))
            rec.state = 'draft'

    def action_print_slip(self):
        return self.env.ref('bank_deposit_prep.action_report_deposit_slip').report_action(self)

    def action_add_payments(self):
        """Open wizard to select outstanding payments."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Add Payments to Deposit'),
            'res_model': 'bank.deposit.add.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_deposit_id': self.id,
                'default_journal_id': self.journal_id.id,
            },
        }
