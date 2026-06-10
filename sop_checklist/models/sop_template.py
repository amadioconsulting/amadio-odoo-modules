from odoo import api, fields, models
from odoo.exceptions import UserError


class SOPTemplate(models.Model):
    _name = 'sop.template'
    _description = 'SOP Template'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Template Name',
        required=True,
        tracking=True,
    )

    code = fields.Char(
        string='Code',
        help='Short template code (e.g., ONBOARD-01)',
        tracking=True,
    )

    category = fields.Char(
        string='Category',
        help='Template category for grouping',
    )

    description = fields.Text(
        string='Description',
        help='Detailed description of this SOP',
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    step_ids = fields.One2many(
        comodel_name='sop.template.step',
        inverse_name='template_id',
        string='Steps',
        copy=True,
    )

    step_count = fields.Integer(
        string='Step Count',
        compute='_compute_step_count',
        store=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )

    applicable_models = fields.Char(
        string='Applicable Models',
        help='Comma-separated list of model names (e.g., sale.order, project.project). Leave empty for all models.',
    )

    # Computed stats
    critical_step_count = fields.Integer(
        string='Critical Steps',
        compute='_compute_critical_step_count',
        store=True,
    )

    checklist_count = fields.Integer(
        string='Checklist Count',
        compute='_compute_checklist_count',
    )

    @api.depends('step_ids')
    def _compute_step_count(self):
        for template in self:
            template.step_count = len(template.step_ids)

    @api.depends('step_ids.is_critical')
    def _compute_critical_step_count(self):
        for template in self:
            template.critical_step_count = len(
                template.step_ids.filtered('is_critical')
            )

    def _compute_checklist_count(self):
        for template in self:
            template.checklist_count = self.env['sop.checklist'].search_count([
                ('template_id', '=', template.id)
            ])

    def action_launch(self):
        """Open wizard to launch this template on a record."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sop.launch.checklist.wizard',
            'view_mode': 'form',
            'context': {
                'default_template_id': self.id,
            },
            'target': 'new',
        }

    def action_duplicate_template(self):
        """Duplicate this template with all its steps."""
        for template in self:
            new_template = template.copy(default={
                'name': f"{template.name} (Copy)",
                'code': f"{template.code or 'COPY'}-{self.id}",
            })
            if template.step_ids:
                for step in template.step_ids:
                    step.copy(default={'template_id': new_template.id})

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sop.template',
                'res_id': new_template.id,
                'view_mode': 'form',
            }

    def action_view_checklists(self):
        """View all checklists created from this template."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sop.checklist',
            'view_mode': 'tree,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

    def get_applicable_models(self):
        """Return list of applicable model names."""
        if not self.applicable_models:
            return None
        return [m.strip() for m in self.applicable_models.split(',')]

    def is_applicable_to_model(self, model_name):
        """Check if this template is applicable to the given model."""
        applicable = self.get_applicable_models()
        if not applicable:
            return True
        return model_name in applicable
