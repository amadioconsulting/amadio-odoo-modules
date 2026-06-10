from odoo import models, fields, api, _
from odoo.tools import html_escape
import logging

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    smart_suggested_template_ids = fields.Many2many(
        'mail.template',
        string='Smart Suggested Templates',
        compute='_compute_suggested_templates',
        help='Templates suggested based on current model and stage'
    )
    smart_recently_used_template_ids = fields.Many2many(
        'mail.template',
        relation='smart_template_recently_used_rel',
        string='Recently Used Templates',
        compute='_compute_recently_used_templates',
        help='Templates recently used by the current user'
    )

    @api.depends('model', 'res_id')
    def _compute_suggested_templates(self):
        """
        Compute smart suggestions based on current model and record.
        Returns up to 5 most relevant templates ordered by priority and usage.
        """
        SmartRule = self.env['smart.mail.template.rule']
        SmartUsage = self.env['smart.mail.template.usage']

        for record in self:
            suggested_templates = self.env['mail.template']

            if not record.model or not record.res_id:
                record.smart_suggested_template_ids = suggested_templates
                continue

            try:
                # Get the model's ir.model record
                model_name = record.model
                ir_model = self.env['ir.model'].search(
                    [('model', '=', model_name)],
                    limit=1
                )

                if not ir_model:
                    record.smart_suggested_template_ids = suggested_templates
                    continue

                # Get the actual record instance
                target_model = self.env[model_name]
                target_record = target_model.browse(record.res_id)

                if not target_record.exists():
                    record.smart_suggested_template_ids = suggested_templates
                    continue

                # Find matching rules
                rules = SmartRule.search(
                    [('model_id', '=', ir_model.id), ('active', '=', True)],
                    order='priority desc'
                )

                # Score each rule: exact match, then by priority, then by usage
                scored_templates = []

                for rule in rules:
                    # Check if stage field matches (if specified)
                    if rule.stage_field and rule.stage_value:
                        if hasattr(target_record, rule.stage_field):
                            field_value = getattr(target_record, rule.stage_field)
                            # Handle both char and many2one fields
                            if hasattr(field_value, 'name'):
                                # many2one: compare name
                                actual_value = field_value.name
                            else:
                                # char/selection: compare directly
                                actual_value = str(field_value) if field_value else ''

                            if actual_value != rule.stage_value:
                                continue
                        else:
                            continue

                    # Get usage frequency for this template/user pair
                    usage = SmartUsage.search(
                        [
                            ('template_id', '=', rule.template_id.id),
                            ('user_id', '=', self.env.user.id),
                        ],
                        limit=1
                    )
                    use_frequency = usage.use_count if usage else 0

                    # Compute score: priority is primary, usage is secondary tiebreaker
                    score = (rule.priority * 1000) + (use_frequency * rule.usage_multiplier)

                    scored_templates.append({
                        'template': rule.template_id,
                        'score': score,
                        'rule_id': rule.id,
                    })

                # Sort by score descending and take top 5
                scored_templates.sort(key=lambda x: x['score'], reverse=True)
                top_templates = [item['template'] for item in scored_templates[:5]]

                # Remove duplicates while preserving order
                seen = set()
                unique_templates = []
                for t in top_templates:
                    if t.id not in seen:
                        unique_templates.append(t.id)
                        seen.add(t.id)

                suggested_templates = self.env['mail.template'].browse(unique_templates)

            except Exception as e:
                _logger.warning(
                    f'Error computing smart templates for {record.model}#{record.res_id}: {str(e)}'
                )

            record.smart_suggested_template_ids = suggested_templates

    @api.depends('model')
    def _compute_recently_used_templates(self):
        """
        Compute recently used templates for the current user.
        Shows the last 5 templates used by this user in the past 30 days.
        """
        SmartUsage = self.env['smart.mail.template.usage']

        for record in self:
            recently_used = self.env['mail.template']

            try:
                usage_records = SmartUsage.get_recently_used(
                    user_id=self.env.user.id,
                    limit=5,
                    days=30
                )
                recently_used = usage_records.mapped('template_id')

            except Exception as e:
                _logger.warning(f'Error computing recently used templates: {str(e)}')

            record.smart_recently_used_template_ids = recently_used

    def _action_apply_template(self, template):
        """
        Override template application to record usage.
        Called when user clicks a suggested or recent template.
        """
        # Record usage before applying
        SmartUsage = self.env['smart.mail.template.usage']
        SmartUsage.record_usage(template.id, self.env.user.id)

        # Call parent implementation to actually apply the template
        return super()._action_apply_template(template)

    def action_apply_suggested_template(self, template_id):
        """
        Action: Apply a suggested template and record usage.
        Called from the view when user clicks a suggested template button.
        """
        template = self.env['mail.template'].browse(template_id)
        if not template.exists():
            return False

        # Record usage
        SmartUsage = self.env['smart.mail.template.usage']
        SmartUsage.record_usage(template.id, self.env.user.id)

        # Apply template to current compose message
        self.template_id = template
        self._onchange_template_id()

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
