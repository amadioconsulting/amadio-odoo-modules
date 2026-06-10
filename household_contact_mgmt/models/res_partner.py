# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    household_id = fields.Many2one(
        'household.household',
        string='Household',
        index=True,
        ondelete='set null',
        tracking=True,
    )
    household_role = fields.Selection([
        ('primary', 'Primary Contact'),
        ('spouse', 'Spouse / Partner'),
        ('child', 'Child'),
        ('dependent', 'Dependent'),
        ('other', 'Other Member'),
    ], string='Household Role', default='primary')
    birth_date = fields.Date(string='Date of Birth')
    baptism_date = fields.Date(string='Baptism / Registration Date')

    # Convenience computed field showing household salutation
    household_display_name = fields.Char(
        string='Household Name',
        related='household_id.display_name',
        store=False,
    )

    @api.onchange('household_id')
    def _onchange_household_id(self):
        """Copy address from household when one is assigned."""
        if self.household_id:
            hh = self.household_id
            if hh.street and not self.street:
                self.street = hh.street
            if hh.street2 and not self.street2:
                self.street2 = hh.street2
            if hh.city and not self.city:
                self.city = hh.city
            if hh.state_id and not self.state_id:
                self.state_id = hh.state_id
            if hh.zip and not self.zip:
                self.zip = hh.zip
            if hh.country_id and not self.country_id:
                self.country_id = hh.country_id
