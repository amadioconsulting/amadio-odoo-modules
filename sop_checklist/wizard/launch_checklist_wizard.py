from odoo import api, fields, models
from odoo.exceptions import UserError


class SOPLaunchChecklistWizard(models.TransientModel):
    _name = 'sop.launch.checklist.wizard'
    _description = 'Launch SOP Checklist Wizard'

    template_id = fields.Many2one(
        comodel_name='sop.template',
        string='SOP Template',
        required=True,
    )

    res_model = fields.Char(
        string='Model',
        required=True,
        help='Model name to launch the checklist on',
    )

    res_id = fields.Integer(
        string='Record ID',
        required=True,
        help='ID of the record to attach this checklist to',
    )

    res_name = fields.Char(
        string='Record Name',
        help='Display name of the record (for reference)',
    )

    notes = fields.Text(
        string='Launch Notes',
        help='Optional notes about why this SOP is being launched',
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Auto-set res_model from active_model in context if not set."""
        if not self.res_model and self.template_id:
            active_model = self.env.context.get('active_model')
            if active_model:
                self.res_model = active_model

    @api.onchange('res_model', 'res_id')
    def _onchange_res_model_id(self):
        """Fetch display name when model and ID are set."""
        if self.res_model and self.res_id:
            try:
                record = self.env[self.res_model].browse(self.res_id)
                if record.exists():
                    self.res_name = record.display_name
                else:
                    raise UserError(f'Record {self.res_id} does not exist in {self.res_model}')
            except (KeyError, ValueError) as e:
                raise UserError(f'Invalid model: {self.res_model}. Error: {str(e)}')

    def action_launch(self):
        """Create checklist instance and copy template steps."""
        for wizard in self:
            # Validate template is applicable to this model
            if not wizard.template_id.is_applicable_to_model(wizard.res_model):
                raise UserError(
                    f'Template "{wizard.template_id.name}" is not applicable to model {wizard.res_model}.\n'
                    f'Applicable models: {wizard.template_id.applicable_models or "All models"}'
                )

            # Create checklist
            checklist = self.env['sop.checklist'].create({
                'template_id': wizard.template_id.id,
                'res_model': wizard.res_model,
                'res_id': wizard.res_id,
                'res_name': wizard.res_name,
            })

            # Copy steps from template
            for template_step in wizard.template_id.step_ids:
                self.env['sop.checklist.step'].create({
                    'checklist_id': checklist.id,
                    'sequence': template_step.sequence,
                    'name': template_step.name,
                    'description': template_step.description,
                    'is_critical': template_step.is_critical,
                    'requires_evidence': template_step.requires_evidence,
                })

            # Log in checklist
            if wizard.notes:
                checklist.message_post(
                    body=f"SOP launched with notes: {wizard.notes}",
                    message_type='notification',
                )

            # Return action to open the new checklist
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sop.checklist',
                'res_id': checklist.id,
                'view_mode': 'form',
            }

        return {}
