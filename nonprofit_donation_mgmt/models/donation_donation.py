from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class DonationDonation(models.Model):
    """
    Model to track individual donations.
    Manages donor information, amounts, payment methods, and generates tax receipts.
    """
    _name = 'donation.donation'
    _description = 'Donation'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Core fields
    donor_id = fields.Many2one(
        'res.partner',
        string='Donor',
        required=True,
        tracking=True,
        help='Donor/contributor contact'
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Date donation was received'
    )
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help='Donation amount'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    # Payment details
    payment_method = fields.Selection(
        selection=[
            ('cash', 'Cash'),
            ('cheque', 'Cheque'),
            ('etransfer', 'E-Transfer'),
            ('card', 'Card'),
            ('other', 'Other'),
        ],
        string='Payment Method',
        default='cash',
        tracking=True,
        help='How the donation was received'
    )
    cheque_number = fields.Char(
        string='Cheque Number',
        help='Cheque number if payment_method is cheque'
    )

    # Categorization
    fund_id = fields.Many2one(
        'donation.fund',
        string='Fund/Purpose',
        help='Restricted fund or purpose for this donation'
    )
    campaign_id = fields.Many2one(
        'donation.campaign',
        string='Campaign',
        help='Fundraising campaign this donation relates to'
    )

    # Tracking & receipting
    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        help='Auto-generated donation reference number'
    )
    receipt_number = fields.Char(
        string='Receipt Number',
        readonly=True,
        copy=False,
        help='Assigned when receipt is generated'
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('receipted', 'Receipted'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        help='Donation workflow state'
    )

    # Accounting
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain="[('type', 'in', ['bank', 'cash', 'general'])]",
        help='Journal for posting accounting entry (optional)'
    )
    move_id = fields.Many2one(
        'account.move',
        string='Accounting Entry',
        readonly=True,
        copy=False,
        help='Journal entry created from this donation'
    )

    # Notes
    note = fields.Text(
        string='Notes',
        help='Additional information about donation'
    )

    _sql_constraints = [
        ('reference_uniq', 'unique(reference)', 'Donation reference must be unique!'),
        ('amount_positive', 'CHECK(amount > 0)', 'Donation amount must be positive!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Assign reference number on creation."""
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('donation.donation')
        return super().create(vals_list)

    @api.constrains('donor_id', 'cheque_number', 'date')
    def _check_cheque_number_unique(self):
        """Ensure cheque numbers are unique per donor (sanity check)."""
        for donation in self:
            if donation.payment_method == 'cheque' and donation.cheque_number:
                duplicates = self.search([
                    ('donor_id', '=', donation.donor_id.id),
                    ('cheque_number', '=', donation.cheque_number),
                    ('payment_method', '=', 'cheque'),
                    ('id', '!=', donation.id),
                ])
                if duplicates:
                    raise ValidationError(
                        f"Cheque #{donation.cheque_number} from {donation.donor_id.name} already recorded."
                    )

    def action_confirm(self):
        """Confirm donation, validating required fields."""
        for donation in self:
            if not donation.donor_id:
                raise ValidationError("Donor is required to confirm a donation.")
            if not donation.amount or donation.amount <= 0:
                raise ValidationError("Donation amount must be greater than zero.")
            donation.state = 'confirmed'
            _logger.info(f"Donation {donation.reference} confirmed by {self.env.user.name}")

    def action_generate_receipt(self):
        """Generate receipt PDF and update state to receipted."""
        for donation in self:
            if donation.state not in ['confirmed', 'receipted']:
                raise UserError("Only confirmed or receipted donations can have receipts generated.")

            if not donation.receipt_number:
                # Generate receipt number from sequence
                donation.receipt_number = self.env['ir.sequence'].next_by_code('donation.receipt')

            donation.state = 'receipted'
            _logger.info(f"Receipt generated for donation {donation.reference}: #{donation.receipt_number}")

        # Return action to print/view PDF
        return {
            'type': 'ir.actions.report',
            'report_name': 'nonprofit_donation_mgmt.report_donation_receipt',
            'model': 'donation.donation',
            'report_type': 'qweb-pdf',
        }

    def action_post_to_accounting(self):
        """Create accounting journal entry for confirmed donation."""
        for donation in self:
            if donation.state not in ['confirmed', 'receipted']:
                raise UserError("Only confirmed or receipted donations can be posted to accounting.")

            if donation.move_id:
                raise UserError(f"Donation {donation.reference} already has an accounting entry.")

            if not donation.journal_id:
                raise UserError("Please select a journal to post this donation.")

            # Build move lines
            move_lines = []

            # Debit: bank/cash account
            move_lines.append((0, 0, {
                'account_id': donation.journal_id.default_account_id.id,
                'debit': donation.amount,
                'credit': 0,
                'name': f"Donation {donation.reference} - {donation.donor_id.name}",
            }))

            # Credit: revenue/donation account (from fund if available)
            credit_account_id = donation.fund_id.account_id.id if donation.fund_id else None
            if not credit_account_id:
                # Fall back to company donation revenue account if it exists
                # For now, we'll require fund selection or journal config
                raise UserError("Fund or journal must be configured with donation account.")

            move_lines.append((0, 0, {
                'account_id': credit_account_id,
                'debit': 0,
                'credit': donation.amount,
                'name': f"Donation {donation.reference} - {donation.donor_id.name}",
            }))

            # Create move
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'journal_id': donation.journal_id.id,
                'date': donation.date,
                'ref': donation.reference,
                'line_ids': move_lines,
            })

            donation.move_id = move.id
            _logger.info(f"Accounting entry {move.name} created for donation {donation.reference}")

    def action_view_accounting_entry(self):
        """View the accounting entry linked to this donation."""
        self.ensure_one()
        if not self.move_id:
            raise UserError("No accounting entry linked to this donation.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accounting Entry',
            'model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }

    def action_set_to_draft(self):
        """Reset donation to draft state."""
        for donation in self:
            if donation.move_id:
                raise UserError("Cannot reset to draft: donation has accounting entry. Delete entry first.")
            donation.state = 'draft'

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        """Clear cheque number if payment method changes away from cheque."""
        if self.payment_method != 'cheque':
            self.cheque_number = False

    def get_donation_summary_for_donor_year(self, donor_id, year):
        """Helper: get all donations for a donor in a given year."""
        from datetime import datetime
        year_start = datetime(year, 1, 1).date()
        year_end = datetime(year, 12, 31).date()

        donations = self.search([
            ('donor_id', '=', donor_id),
            ('state', '=', 'receipted'),
            ('date', '>=', year_start),
            ('date', '<=', year_end),
        ], order='date asc')

        return donations

    def action_print_receipt(self):
        """Action to print receipt for current donation."""
        self.ensure_one()
        if not self.receipt_number:
            raise UserError("Receipt must be generated before printing.")

        return {
            'type': 'ir.actions.report',
            'report_name': 'nonprofit_donation_mgmt.report_donation_receipt',
            'model': 'donation.donation',
            'report_type': 'qweb-pdf',
        }
