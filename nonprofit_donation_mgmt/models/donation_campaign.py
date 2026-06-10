from odoo import models, fields, api
from datetime import datetime


class DonationCampaign(models.Model):
    """
    Model to represent fundraising campaigns.
    Campaigns can have start/end dates and fundraising goals.
    """
    _name = 'donation.campaign'
    _description = 'Donation Campaign'
    _order = 'date_start desc, name'

    name = fields.Char(
        string='Campaign Name',
        required=True,
        help='Name of the fundraising campaign'
    )
    date_start = fields.Date(
        string='Start Date',
        help='Campaign launch date'
    )
    date_end = fields.Date(
        string='End Date',
        help='Campaign completion date'
    )
    goal_amount = fields.Monetary(
        string='Fundraising Goal',
        help='Target amount to raise in this campaign',
        currency_field='currency_id'
    )
    fund_id = fields.Many2one(
        'donation.fund',
        string='Fund',
        help='Fund to which campaign donations are designated'
    )
    description = fields.Text(
        string='Description',
        help='Campaign details and purpose'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Inactive campaigns will not appear in dropdowns'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    # Computed fields
    total_raised = fields.Monetary(
        string='Total Raised',
        compute='_compute_total_raised',
        currency_field='currency_id',
        help='Total amount donated to this campaign'
    )
    donation_count = fields.Integer(
        string='Number of Donations',
        compute='_compute_donation_count'
    )
    progress_percent = fields.Float(
        string='Progress %',
        compute='_compute_progress_percent',
        help='Percentage of goal reached'
    )
    is_active_campaign = fields.Boolean(
        string='Campaign Active Now',
        compute='_compute_is_active_campaign'
    )

    @api.depends('name')
    def _compute_total_raised(self):
        for campaign in self:
            donations = self.env['donation.donation'].search(
                [('campaign_id', '=', campaign.id), ('state', '=', 'receipted')]
            )
            campaign.total_raised = sum(donations.mapped('amount'))

    @api.depends('name')
    def _compute_donation_count(self):
        for campaign in self:
            campaign.donation_count = self.env['donation.donation'].search_count(
                [('campaign_id', '=', campaign.id), ('state', '=', 'receipted')]
            )

    @api.depends('total_raised', 'goal_amount')
    def _compute_progress_percent(self):
        for campaign in self:
            if campaign.goal_amount > 0:
                campaign.progress_percent = (campaign.total_raised / campaign.goal_amount) * 100
            else:
                campaign.progress_percent = 0.0

    @api.depends('date_start', 'date_end')
    def _compute_is_active_campaign(self):
        today = datetime.now().date()
        for campaign in self:
            start_ok = not campaign.date_start or campaign.date_start <= today
            end_ok = not campaign.date_end or campaign.date_end >= today
            campaign.is_active_campaign = start_ok and end_ok
