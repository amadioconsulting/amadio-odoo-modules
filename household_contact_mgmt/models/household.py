# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Household(models.Model):
    _name = 'household.household'
    _description = 'Household'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'family_name, id'
    _rec_name = 'display_name'

    family_name = fields.Char(
        string='Family Name',
        required=True,
        tracking=True,
        help='The shared surname of the household (e.g. "Smith").',
    )
    display_name = fields.Char(
        string='Household Name',
        compute='_compute_display_name',
        store=True,
        help='Auto-generated combined salutation.',
    )
    salutation_override = fields.Char(
        string='Salutation Override',
        tracking=True,
        help='Override the auto-generated salutation (e.g. "The Smith-Jones Family").',
    )
    partner_ids = fields.One2many(
        'res.partner',
        'household_id',
        string='Members',
    )
    primary_partner_id = fields.Many2one(
        'res.partner',
        string='Primary Contact',
        compute='_compute_primary_partner',
        store=True,
        help='The primary contact for this household (role = Primary).',
    )
    # Address — stored on the household, inherited by members
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State/Province')
    zip = fields.Char(string='ZIP / Postal Code')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Household Phone')
    email = fields.Char(string='Household Email')

    # Milestones
    anniversary_date = fields.Date(string='Wedding Anniversary', tracking=True)
    membership_since = fields.Date(string='Member / Parishioner Since', tracking=True)
    notes = fields.Text(string='Notes')

    active = fields.Boolean(default=True)

    @api.depends('salutation_override', 'family_name', 'partner_ids',
                 'partner_ids.name', 'partner_ids.household_role',
                 'partner_ids.title')
    def _compute_display_name(self):
        for rec in self:
            if rec.salutation_override:
                rec.display_name = rec.salutation_override
                continue

            primaries = rec.partner_ids.filtered(
                lambda p: p.household_role == 'primary'
            )
            spouses = rec.partner_ids.filtered(
                lambda p: p.household_role == 'spouse'
            )

            if primaries and spouses:
                # "Mr. & Mrs. Smith" style
                p_first = (primaries[0].name or '').split()[0] if primaries[0].name else ''
                s_first = (spouses[0].name or '').split()[0] if spouses[0].name else ''
                if p_first and s_first:
                    rec.display_name = f'{p_first} & {s_first} {rec.family_name}'
                else:
                    rec.display_name = f'The {rec.family_name} Family'
            elif primaries:
                rec.display_name = f'The {primaries[0].name} Household' if primaries[0].name else f'The {rec.family_name} Family'
            else:
                rec.display_name = f'The {rec.family_name} Family'

    @api.depends('partner_ids', 'partner_ids.household_role')
    def _compute_primary_partner(self):
        for rec in self:
            primaries = rec.partner_ids.filtered(
                lambda p: p.household_role == 'primary'
            )
            rec.primary_partner_id = primaries[0] if primaries else False

    def action_view_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Household Members — %s') % self.display_name,
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('household_id', '=', self.id)],
            'context': {'default_household_id': self.id},
        }
