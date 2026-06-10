from odoo import models, fields, api


class DonationFund(models.Model):
    """
    Model to represent donation funds/restricted purpose areas.
    Donations can be designated for specific funds (e.g., Building Fund, Scholarship Fund).
    """
    _name = 'donation.fund'
    _description = 'Donation Fund'
    _order = 'name'

    name = fields.Char(
        string='Fund Name',
        required=True,
        help='Name of the donation fund or restricted purpose'
    )
    code = fields.Char(
        string='Fund Code',
        help='Short code/reference for this fund'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of the fund purpose'
    )
    account_id = fields.Many2one(
        'account.account',
        string='GL Account',
        help='General Ledger account for posting donations to this fund'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Inactive funds will not appear in dropdowns'
    )

    # Computed fields
    donation_count = fields.Integer(
        string='Number of Donations',
        compute='_compute_donation_count'
    )
    total_amount = fields.Monetary(
        string='Total Raised',
        compute='_compute_total_amount',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_currency_id'
    )

    @api.depends('name')
    def _compute_donation_count(self):
        for fund in self:
            fund.donation_count = self.env['donation.donation'].search_count(
                [('fund_id', '=', fund.id), ('state', '=', 'receipted')]
            )

    @api.depends('name')
    def _compute_total_amount(self):
        for fund in self:
            donations = self.env['donation.donation'].search(
                [('fund_id', '=', fund.id), ('state', '=', 'receipted')]
            )
            fund.total_amount = sum(donations.mapped('amount'))

    def _compute_currency_id(self):
        for fund in self:
            fund.currency_id = self.env.company.currency_id
