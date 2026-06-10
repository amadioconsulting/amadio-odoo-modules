from odoo import api, fields, models


class SOPChecklistStep(models.Model):
    _name = 'sop.checklist.step'
    _description = 'SOP Checklist Step'
    _order = 'checklist_id, sequence, id'

    checklist_id = fields.Many2one(
        comodel_name='sop.checklist',
        string='Checklist',
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
    )

    description = fields.Text(
        string='Detailed Description',
    )

    is_critical = fields.Boolean(
        string='Critical Step',
        default=False,
    )

    requires_evidence = fields.Boolean(
        string='Requires Evidence',
        default=False,
    )

    done = fields.Boolean(
        string='Completed',
        default=False,
        tracking=True,
    )

    done_by_id = fields.Many2one(
        comodel_name='res.users',
        string='Completed By',
        tracking=True,
    )

    done_date = fields.Datetime(
        string='Completed On',
        tracking=True,
    )

    evidence_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Evidence Attachment',
        help='File attachment as proof of step completion',
    )

    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about this step',
    )

    @api.onchange('done')
    def _onchange_done(self):
        """When step is marked done, record user and timestamp."""
        if self.done and not self.done_by_id:
            self.done_by_id = self.env.user.id
            self.done_date = fields.Datetime.now()
        elif not self.done:
            # If unmarking as done, clear the completion info
            self.done_by_id = None
            self.done_date = None
            self.evidence_attachment_id = None

    @api.model_create_multi
    def create(self, vals_list):
        """Create checklist steps from template."""
        result = super().create(vals_list)
        return result
