# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    budget_enabled = fields.Boolean(
        string='Enable Budget Control',
        default=False,
        help='Enable budget thresholds and alerts for this analytic account.'
    )
    budget_amount = fields.Monetary(
        string='Budget Amount',
        currency_field='company_currency_id',
        help='Total budget allocated to this analytic account.'
    )
    budget_period = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
            ('year', 'Annual'),
            ('custom', 'Custom Date Range'),
        ],
        string='Budget Period',
        default='month',
        help='Budget calculation period.'
    )
    budget_date_from = fields.Date(
        string='Budget Period From',
        help='Start date for custom budget period.'
    )
    budget_date_to = fields.Date(
        string='Budget Period To',
        help='End date for custom budget period.'
    )
    budget_warn_pct = fields.Float(
        string='Warn Threshold (%)',
        default=80.0,
        help='Send alert email when spending reaches this percentage of budget.'
    )
    budget_block_pct = fields.Float(
        string='Block Threshold (%)',
        default=100.0,
        help='Prevent posting of transactions that exceed this percentage of budget.'
    )
    budget_alert_partner_ids = fields.Many2many(
        'res.partner',
        'analytic_account_budget_alert_partner',
        'account_id',
        'partner_id',
        string='Alert Recipients',
        help='Partners to receive budget warning emails.'
    )
    budget_spent = fields.Monetary(
        string='Amount Spent',
        currency_field='company_currency_id',
        compute='_compute_budget_spent',
        help='Total amount spent in current budget period.'
    )
    budget_remaining = fields.Monetary(
        string='Budget Remaining',
        currency_field='company_currency_id',
        compute='_compute_budget_remaining',
        help='Remaining budget amount.'
    )
    budget_pct_spent = fields.Float(
        string='Percent Spent',
        compute='_compute_budget_pct_spent',
        help='Percentage of budget spent.'
    )
    budget_last_alert_date = fields.Date(
        string='Last Alert Date',
        help='Date of last budget alert sent (used to avoid duplicate daily alerts).'
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.depends('budget_enabled', 'budget_amount')
    def _compute_budget_spent(self):
        """Calculate total spent in current budget period."""
        for account in self:
            if not account.budget_enabled or not account.budget_amount:
                account.budget_spent = 0.0
                continue

            date_from, date_to = account._get_period_dates()

            # Sum credit - debit from analytic lines in period
            spent = 0.0
            domain = [
                ('account_id', '=', account.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ]

            # Query the account_analytic_line model
            analytic_lines = self.env['account.analytic.line'].search(domain)
            for line in analytic_lines:
                spent += line.credit - line.debit

            account.budget_spent = spent

    @api.depends('budget_amount', 'budget_spent')
    def _compute_budget_remaining(self):
        """Calculate remaining budget."""
        for account in self:
            account.budget_remaining = account.budget_amount - account.budget_spent

    @api.depends('budget_amount', 'budget_spent')
    def _compute_budget_pct_spent(self):
        """Calculate percentage of budget spent."""
        for account in self:
            if account.budget_amount > 0:
                account.budget_pct_spent = (account.budget_spent / account.budget_amount) * 100.0
            else:
                account.budget_pct_spent = 0.0

    def _get_period_dates(self):
        """
        Return (date_from, date_to) tuple based on budget_period.

        Returns:
            tuple: (date_from, date_to) as date objects
        """
        self.ensure_one()
        today = date.today()

        if self.budget_period == 'month':
            date_from = today.replace(day=1)
            date_to = (date_from + relativedelta(months=1)) - timedelta(days=1)
        elif self.budget_period == 'quarter':
            quarter = (today.month - 1) // 3
            date_from = date(today.year, quarter * 3 + 1, 1)
            date_to = (date_from + relativedelta(months=3)) - timedelta(days=1)
        elif self.budget_period == 'year':
            date_from = date(today.year, 1, 1)
            date_to = date(today.year, 12, 31)
        elif self.budget_period == 'custom':
            date_from = self.budget_date_from or today
            date_to = self.budget_date_to or today
        else:
            date_from = today
            date_to = today

        return date_from, date_to

    def _send_budget_alert(self, pct_spent, threshold_type='warn'):
        """
        Send email alert to budget_alert_partner_ids.

        Args:
            pct_spent (float): Percentage of budget spent
            threshold_type (str): 'warn' or 'block'
        """
        self.ensure_one()

        if not self.budget_alert_partner_ids:
            return

        today = date.today()

        # Avoid sending duplicate alerts on the same day
        if self.budget_last_alert_date == today:
            return

        threshold_pct = self.budget_warn_pct if threshold_type == 'warn' else self.budget_block_pct

        subject = f"Budget Alert: {self.name} ({threshold_type.upper()})"

        body = f"""
<p>Budget threshold alert for analytic account <strong>{self.name}</strong></p>

<p><strong>Threshold Type:</strong> {threshold_type.upper()}</p>
<p><strong>Budget Amount:</strong> {self.budget_amount:.2f} {self.company_currency_id.symbol}</p>
<p><strong>Amount Spent:</strong> {self.budget_spent:.2f} {self.company_currency_id.symbol}</p>
<p><strong>Percent Spent:</strong> {pct_spent:.1f}%</p>
<p><strong>Threshold:</strong> {threshold_pct:.1f}%</p>
<p><strong>Period:</strong> {self.budget_period}</p>

<p>Please review spending on this account and take appropriate action.</p>
"""

        # Create mail message for each partner
        for partner in self.budget_alert_partner_ids:
            self.env['mail.mail'].create({
                'subject': subject,
                'body_html': body,
                'email_to': partner.email,
                'email_from': self.env.user.company_id.email or self.env.user.email,
            }).send()

        # Update last alert date
        self.budget_last_alert_date = today

    @api.constrains('budget_warn_pct', 'budget_block_pct')
    def _check_budget_thresholds(self):
        """Ensure warn % is less than block %."""
        for account in self:
            if account.budget_warn_pct > account.budget_block_pct:
                raise UserError(
                    f"Warn threshold ({account.budget_warn_pct}%) must be less than or equal to "
                    f"block threshold ({account.budget_block_pct}%)."
                )

    @api.constrains('budget_period', 'budget_date_from', 'budget_date_to')
    def _check_budget_period_dates(self):
        """Ensure custom period dates are valid."""
        for account in self:
            if account.budget_period == 'custom':
                if not account.budget_date_from or not account.budget_date_to:
                    raise UserError(
                        "Custom budget period requires both 'From' and 'To' dates."
                    )
                if account.budget_date_from > account.budget_date_to:
                    raise UserError(
                        "'Budget Period From' must be before 'Budget Period To'."
                    )
