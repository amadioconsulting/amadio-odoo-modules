# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from decimal import Decimal

from odoo import api, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _check_analytic_budget(self, analytic_account, amount):
        """
        Check if posting this line would exceed budget thresholds.

        Args:
            analytic_account (account.analytic.account): The analytic account
            amount (float): The amount being posted

        Raises:
            UserError: If amount exceeds block threshold
        """
        if not analytic_account.budget_enabled or not analytic_account.budget_amount:
            return

        # Calculate what the total spent would be after this posting
        would_be_spent = analytic_account.budget_spent + amount
        would_be_pct = (would_be_spent / analytic_account.budget_amount * 100.0) if analytic_account.budget_amount > 0 else 0.0

        # Check block threshold first
        if would_be_pct > analytic_account.budget_block_pct:
            raise UserError(
                f"Cannot post: Amount would exceed budget block threshold for analytic account '{analytic_account.name}'. "
                f"Current spend: {analytic_account.budget_spent:.2f} {analytic_account.company_currency_id.symbol}, "
                f"Block threshold: {analytic_account.budget_block_pct}%, "
                f"Would-be percent: {would_be_pct:.1f}%"
            )

        # Check warn threshold and send alert
        if would_be_pct > analytic_account.budget_warn_pct:
            analytic_account._send_budget_alert(would_be_pct, threshold_type='warn')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate budget on new lines."""
        lines = super().create(vals_list)

        # We'll check budget when the move is posted, not on creation
        return lines

    def write(self, vals):
        """Override write to check budget when move is posted."""
        result = super().write(vals)

        # Check if we're changing the move state to 'posted'
        if 'move_id' in vals or any(self.mapped('move_id.state')):
            for line in self:
                move = line.move_id
                # Only check if move is being posted
                if move.state == 'posted':
                    self._check_budget_on_line(line)

        return result

    def _check_budget_on_line(self, line):
        """
        Check budget thresholds for a single account move line.

        Args:
            line (account.move.line): The line to check
        """
        # Get analytic account from analytic_distribution or account_id
        analytic_account = None

        # Check if there's an analytic_distribution (newer Odoo versions)
        if hasattr(line, 'analytic_distribution') and line.analytic_distribution:
            # analytic_distribution is a dict: {account_id: percentage}
            for account_id_str in line.analytic_distribution.keys():
                try:
                    account_id = int(account_id_str)
                    analytic_account = self.env['account.analytic.account'].browse(account_id)
                    if analytic_account.exists():
                        # Use the percentage allocation
                        percentage = line.analytic_distribution[account_id_str]
                        allocated_amount = (line.balance * percentage / 100.0) if percentage else line.balance
                        self._check_analytic_budget(analytic_account, abs(allocated_amount))
                except (ValueError, TypeError):
                    pass

        # Fallback: check account_id field
        elif hasattr(line, 'account_id') and line.account_id:
            analytic_account = line.account_id
            if analytic_account.budget_enabled:
                self._check_analytic_budget(analytic_account, abs(line.balance))

    @api.model
    def _check_budget_on_move_post(self, move):
        """
        Check budget for all analytic lines on a move being posted.

        This is called from the move model when posting.

        Args:
            move (account.move): The move being posted
        """
        for line in move.line_ids:
            self._check_budget_on_line(line)
