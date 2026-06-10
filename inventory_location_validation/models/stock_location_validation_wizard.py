from odoo import models, fields, api


class StockLocationValidationWizard(models.TransientModel):
    _name = 'stock.location.validation.wizard'
    _description = 'Stock Location Validation Confirmation Wizard'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Stock Picking',
        required=True,
        readonly=True
    )
    violation_text = fields.Text(
        string='Violations',
        readonly=True,
        help='Details of location rule violations found'
    )

    def action_confirm(self):
        """User confirms and wants to proceed despite warnings."""
        self.ensure_one()
        picking = self.picking_id
        # Proceed with validation by calling the parent model's button_validate
        # This bypasses our override by directly calling super()
        result = super(type(picking), picking).button_validate()
        return result

    def action_cancel(self):
        """User cancels the operation."""
        return {'type': 'ir.actions.act_window_close'}
