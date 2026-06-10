from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SmartMailTemplateRule(models.Model):
    _name = 'smart.mail.template.rule'
    _description = 'Smart Mail Template Rule'
    _order = 'priority desc, id desc'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='The model for which this rule applies (e.g., sale.order, crm.lead)'
    )
    template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        required=True,
        ondelete='cascade',
        help='The email template to suggest'
    )
    stage_field = fields.Char(
        string='Stage Field',
        help='Field name to match (e.g., "state", "stage_id"). Leave blank to always suggest.'
    )
    stage_value = fields.Char(
        string='Stage Value',
        help='Value to match (e.g., "confirmed", "1"). Used if Stage Field is specified.'
    )
    priority = fields.Integer(
        string='Priority',
        default=50,
        help='Priority order (0–100). Higher priority templates appear first.'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Enable or disable this rule'
    )
    usage_multiplier = fields.Float(
        string='Usage Multiplier',
        default=1.0,
        help='Multiplier applied to usage frequency scoring (0.1–10.0)'
    )
    created_date = fields.Datetime(
        string='Created',
        readonly=True,
        default=lambda self: fields.Datetime.now()
    )
    notes = fields.Text(
        string='Notes',
        help='Internal notes about this rule'
    )

    _sql_constraints = [
        (
            'priority_range',
            'CHECK(priority >= 0 AND priority <= 100)',
            'Priority must be between 0 and 100'
        ),
        (
            'usage_multiplier_range',
            'CHECK(usage_multiplier >= 0.1 AND usage_multiplier <= 10.0)',
            'Usage multiplier must be between 0.1 and 10.0'
        ),
    ]

    @api.constrains('stage_field', 'stage_value')
    def _check_stage_consistency(self):
        for record in self:
            if (record.stage_field and not record.stage_value) or \
               (not record.stage_field and record.stage_value):
                raise ValidationError(
                    _('Both Stage Field and Stage Value must be specified together, or both left blank.')
                )

    def name_get(self):
        result = []
        for record in self:
            model_name = record.model_id.name
            template_name = record.template_id.name
            if record.stage_field and record.stage_value:
                name = f'{model_name} / {record.stage_field}={record.stage_value} -> {template_name} (P{record.priority})'
            else:
                name = f'{model_name} -> {template_name} (P{record.priority})'
            result.append((record.id, name))
        return result

    def action_test_rule(self):
        """Test rule: show which templates would be suggested for a test model instance."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'smart.mail.template.rule',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
