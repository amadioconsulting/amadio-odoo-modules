from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class DonationYearEndWizard(models.TransientModel):
    """
    Wizard to generate year-end donation statements.
    Select donor and year, generates PDF with all donations in that year.
    """
    _name = 'donation.year.end.wizard'
    _description = 'Year-End Donation Statement Wizard'

    donor_id = fields.Many2one(
        'res.partner',
        string='Donor',
        required=True,
        help='Select donor to generate statement for'
    )
    year = fields.Integer(
        string='Tax Year',
        required=True,
        default=lambda self: datetime.now().year - 1,
        help='Tax year for which to generate statement'
    )
    total_donations = fields.Monetary(
        string='Total Donations',
        compute='_compute_total_donations',
        currency_field='currency_id',
        readonly=True
    )
    donation_count = fields.Integer(
        string='Number of Donations',
        compute='_compute_donation_count',
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('donor_id', 'year')
    def _compute_total_donations(self):
        for wizard in self:
            donations = self._get_year_donations()
            wizard.total_donations = sum(donations.mapped('amount'))

    @api.depends('donor_id', 'year')
    def _compute_donation_count(self):
        for wizard in self:
            donations = self._get_year_donations()
            wizard.donation_count = len(donations)

    def _get_year_donations(self):
        """Get all receipted donations for donor in selected year."""
        self.ensure_one()
        year_start = datetime(self.year, 1, 1).date()
        year_end = datetime(self.year, 12, 31).date()

        donations = self.env['donation.donation'].search([
            ('donor_id', '=', self.donor_id.id),
            ('state', '=', 'receipted'),
            ('date', '>=', year_start),
            ('date', '<=', year_end),
        ], order='date asc')

        return donations

    def action_generate_statement(self):
        """Generate PDF statement for donations in selected year."""
        self.ensure_one()

        donations = self._get_year_donations()
        if not donations:
            raise UserError(
                f"No receipted donations found for {self.donor_id.name} in {self.year}."
            )

        # Create a context to pass donor_id and year to the report
        return {
            'type': 'ir.actions.report',
            'report_name': 'nonprofit_donation_mgmt.report_donation_year_end',
            'model': 'donation.donation',
            'report_type': 'qweb-pdf',
            'context': {
                'donor_id': self.donor_id.id,
                'year': self.year,
            }
        }

    def action_generate_csv(self):
        """Generate CSV export of donations for the selected year."""
        self.ensure_one()

        donations = self._get_year_donations()
        if not donations:
            raise UserError(
                f"No receipted donations found for {self.donor_id.name} in {self.year}."
            )

        # For now, return action to download; actual CSV generation
        # would be handled by a custom server action or controller
        return {
            'type': 'ir.actions.act_window_close',
        }
