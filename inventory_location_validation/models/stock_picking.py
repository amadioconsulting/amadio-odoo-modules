from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    has_location_violations = fields.Boolean(
        compute='_compute_has_location_violations',
        store=False,
        help='Indicates if this picking has location rule violations'
    )
    location_violation_count = fields.Integer(
        compute='_compute_has_location_violations',
        store=False,
        help='Count of location rule violations'
    )

    @api.depends('move_ids', 'move_ids.location_dest_id', 'move_ids.product_id')
    def _compute_has_location_violations(self):
        """Compute whether this picking has location violations."""
        for picking in self:
            violations = self._check_location_violations(picking.move_ids)
            picking.has_location_violations = len(violations) > 0
            picking.location_violation_count = len(violations)

    def _check_location_violations(self, move_lines):
        """
        Check move lines against location rules.
        Returns a list of violation dicts.
        """
        location_rule_obj = self.env['stock.location.rule']
        return location_rule_obj._get_violations(move_lines)

    def button_validate(self):
        """
        Override the standard validate button to check location rules.
        If violations exist and action='block', raise UserError.
        If violations exist and action='warn', show confirmation wizard.
        """
        self.ensure_one()

        # Get all move lines to validate
        move_lines = self.move_ids
        if not move_lines:
            return super().button_validate()

        # Check for violations
        violations = self._check_location_violations(move_lines)

        if not violations:
            # No violations, proceed normally
            return super().button_validate()

        # Separate violations by action
        block_violations = [v for v in violations if v['action'] == 'block']
        warn_violations = [v for v in violations if v['action'] == 'warn']

        # If any block rules are violated, raise an error
        if block_violations:
            error_msg = 'Location Validation Error:\n\n'
            for violation in block_violations:
                error_msg += (
                    f"Product: {violation['product_name']}\n"
                    f"Category: {violation['category_name']}\n"
                    f"Destination: {violation['destination_location']}\n"
                    f"Reason: {violation['note'] or 'Restricted location for this category'}\n\n"
                )
            error_msg += 'This picking cannot be validated due to location restrictions. Contact your manager.'
            raise UserError(error_msg)

        # If only warn violations, show confirmation dialog
        if warn_violations:
            wizard = self.env['stock.location.validation.wizard'].create({
                'picking_id': self.id,
                'violation_text': self._format_violations_for_wizard(warn_violations),
            })
            return {
                'name': 'Location Validation Warning',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.location.validation.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
            }

        return super().button_validate()

    def _format_violations_for_wizard(self, violations):
        """Format violations into a readable string for the wizard."""
        text = 'The following products are being moved to restricted locations:\n\n'
        for i, violation in enumerate(violations, 1):
            text += (
                f"{i}. {violation['product_name']}\n"
                f"   Category: {violation['category_name']}\n"
                f"   To: {violation['destination_location']}\n"
                f"   Note: {violation['note'] or 'Location restricted for this category'}\n\n"
            )
        text += '\nDo you want to continue with validation despite these warnings?'
        return text
