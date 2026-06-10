from odoo import api, fields, models
from odoo.exceptions import UserError


class SOPChecklist(models.Model):
    _name = 'sop.checklist'
    _description = 'SOP Checklist Instance'
    _order = 'date_started desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Checklist Name',
        required=True,
        tracking=True,
    )

    template_id = fields.Many2one(
        comodel_name='sop.template',
        string='SOP Template',
        required=True,
        ondelete='restrict',
        tracking=True,
    )

    res_model = fields.Char(
        string='Linked Model',
        required=True,
        help='Model name of the linked record (e.g., sale.order)',
    )

    res_id = fields.Integer(
        string='Linked Record ID',
        required=True,
        help='ID of the linked record',
    )

    res_name = fields.Char(
        string='Linked Record',
        help='Display name of the linked record (stored for reference)',
    )

    state = fields.Selection(
        string='State',
        selection=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='in_progress',
        tracking=True,
    )

    step_ids = fields.One2many(
        comodel_name='sop.checklist.step',
        inverse_name='checklist_id',
        string='Steps',
        copy=False,
    )

    completion_pct = fields.Float(
        string='Completion %',
        compute='_compute_completion_pct',
        store=True,
    )

    steps_done = fields.Integer(
        string='Steps Done',
        compute='_compute_steps_done',
        store=True,
    )

    steps_total = fields.Integer(
        string='Total Steps',
        compute='_compute_steps_total',
        store=True,
    )

    critical_steps_pending = fields.Boolean(
        string='Critical Steps Pending',
        compute='_compute_critical_steps_pending',
        store=True,
    )

    started_by_id = fields.Many2one(
        comodel_name='res.users',
        string='Started By',
        default=lambda self: self.env.user,
        tracking=True,
    )

    date_started = fields.Datetime(
        string='Date Started',
        default=fields.Datetime.now,
        tracking=True,
    )

    date_completed = fields.Datetime(
        string='Date Completed',
        tracking=True,
    )

    # Additional tracking info
    _sql_constraints = [
        ('positive_res_id', 'CHECK(res_id > 0)', 'Record ID must be positive'),
        ('valid_completion_pct', 'CHECK(completion_pct >= 0 AND completion_pct <= 100)', 'Completion % must be 0-100'),
    ]

    @api.depends('step_ids.done')
    def _compute_steps_done(self):
        for checklist in self:
            checklist.steps_done = len(checklist.step_ids.filtered('done'))

    @api.depends('step_ids')
    def _compute_steps_total(self):
        for checklist in self:
            checklist.steps_total = len(checklist.step_ids)

    @api.depends('steps_done', 'steps_total')
    def _compute_completion_pct(self):
        for checklist in self:
            if checklist.steps_total > 0:
                checklist.completion_pct = (checklist.steps_done / checklist.steps_total) * 100
            else:
                checklist.completion_pct = 0.0

    @api.depends('step_ids.done', 'step_ids.is_critical')
    def _compute_critical_steps_pending(self):
        for checklist in self:
            critical_steps = checklist.step_ids.filtered('is_critical')
            checklist.critical_steps_pending = bool(
                critical_steps.filtered(lambda s: not s.done)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals and 'template_id' in vals:
                template = self.env['sop.template'].browse(vals['template_id'])
                res_model = vals.get('res_model', '')
                res_id = vals.get('res_id', '')
                res_name = vals.get('res_name', '')

                # Try to get the display name from the linked record
                if res_model and res_id and not res_name:
                    try:
                        linked_record = self.env[res_model].browse(res_id)
                        if linked_record.exists():
                            res_name = linked_record.display_name
                            vals['res_name'] = res_name
                    except (KeyError, ValueError):
                        pass

                vals['name'] = f"{template.name} — {res_name or res_model}"

        return super().create(vals_list)

    def action_complete(self):
        """Mark checklist as completed after validating critical steps."""
        for checklist in self:
            if checklist.state == 'completed':
                raise UserError('This checklist is already completed.')

            # Check for pending critical steps
            pending_critical = checklist.step_ids.filtered(
                lambda s: s.is_critical and not s.done
            )
            if pending_critical:
                raise UserError(
                    f'Cannot complete checklist. {len(pending_critical)} critical step(s) still pending:\n\n'
                    + '\n'.join(f"• {step.name}" for step in pending_critical)
                )

            # Mark as completed
            checklist.write({
                'state': 'completed',
                'date_completed': fields.Datetime.now(),
            })

            # Log activity
            checklist.message_post(
                body=f"Checklist completed by {self.env.user.name}",
                message_type='notification',
            )

    def action_cancel(self):
        """Cancel the checklist."""
        for checklist in self:
            if checklist.state == 'cancelled':
                raise UserError('This checklist is already cancelled.')

            checklist.write({'state': 'cancelled'})

            checklist.message_post(
                body=f"Checklist cancelled by {self.env.user.name}",
                message_type='notification',
            )

    def action_reopen(self):
        """Reopen a cancelled or completed checklist."""
        for checklist in self:
            checklist.write({
                'state': 'in_progress',
                'date_completed': None,
            })
            checklist.message_post(
                body=f"Checklist reopened by {self.env.user.name}",
                message_type='notification',
            )

    def get_linked_record(self):
        """Get the linked record for this checklist."""
        self.ensure_one()
        try:
            return self.env[self.res_model].browse(self.res_id)
        except (KeyError, ValueError):
            return None

    def action_open_linked_record(self):
        """Open the linked record."""
        self.ensure_one()
        linked = self.get_linked_record()
        if not linked or not linked.exists():
            raise UserError('The linked record no longer exists.')

        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
        }
