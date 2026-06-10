from odoo import api, fields, models


class SOPTemplateStep(models.Model):
    _name = 'sop.template.step'
    _description = 'SOP Template Step'
    _order = 'template_id, sequence, id'

    template_id = fields.Many2one(
        comodel_name='sop.template',
        string='Template',
        required=True,
        ondelete='cascade',
        index=True,
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    name = fields.Char(
        string='Step Instruction',
        required=True,
        help='Clear, concise instruction for this step',
    )

    description = fields.Text(
        string='Detailed Description',
        help='How-to notes, tips, or detailed guidance for completing this step',
    )

    is_critical = fields.Boolean(
        string='Critical Step',
        default=False,
        help='If checked, this step must be completed before the checklist can be marked complete',
    )

    requires_evidence = fields.Boolean(
        string='Requires Evidence',
        default=False,
        help='If checked, an attachment must be provided to mark this step complete',
    )

    responsible_role = fields.Char(
        string='Responsible Role',
        help='Optional: guideline on who should perform this step (e.g., "Manager", "QA Team")',
    )

    estimated_minutes = fields.Integer(
        string='Estimated Time (minutes)',
        help='Estimate how many minutes this step should take',
    )

    # Tracking
    _sql_constraints = [
        ('sequence_positive', 'CHECK(sequence >= 0)', 'Sequence must be >= 0'),
        ('estimated_minutes_positive', 'CHECK(estimated_minutes >= 0)', 'Estimated minutes must be >= 0'),
    ]

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Auto-assign next sequence when template changes."""
        if self.template_id and not self.sequence:
            max_sequence = max(
                (step.sequence for step in self.template_id.step_ids),
                default=0
            )
            self.sequence = max_sequence + 10
