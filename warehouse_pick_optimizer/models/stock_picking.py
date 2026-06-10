from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_optimizable = fields.Boolean(
        compute='_compute_is_optimizable',
        help='True if this picking can be optimized (outgoing or internal transfer)'
    )

    @api.depends('picking_type_code')
    def _compute_is_optimizable(self):
        for picking in self:
            picking.is_optimizable = picking.picking_type_code in ('outgoing', 'internal')

    def action_optimize_pick_path(self):
        """
        Reorder stock.move.line records by location sequence (pick_sequence),
        then by location complete_name for stable, optimized picking order.
        """
        for picking in self:
            if not picking.is_optimizable:
                continue

            # Collect all move lines and sort by location pick_sequence and complete_name
            move_lines = picking.move_line_ids
            if not move_lines:
                continue

            # Create a list of (move_line, sort_key) tuples
            lines_with_key = []
            for line in move_lines:
                location = line.location_id
                # Primary sort: pick_sequence (lower first)
                # Secondary sort: complete_name (alphabetical)
                sort_key = (location.pick_sequence, location.complete_name)
                lines_with_key.append((line, sort_key))

            # Sort by the key
            lines_with_key.sort(key=lambda x: x[1])

            # Reorder move lines by updating their sequence
            for index, (line, _) in enumerate(lines_with_key):
                line.sequence = index

    def _get_optimized_move_lines(self):
        """
        Returns move lines in optimized order (by location sequence and name).
        Used by the pick list report template.
        """
        self.ensure_one()
        move_lines = self.move_line_ids
        if not move_lines:
            return move_lines

        # Sort by location pick_sequence and complete_name
        sorted_lines = sorted(
            move_lines,
            key=lambda x: (x.location_id.pick_sequence, x.location_id.complete_name)
        )
        return sorted_lines

    def action_report_optimized_pick_list(self):
        """
        Generate and return the optimized pick list PDF report.
        """
        return self.env.ref('warehouse_pick_optimizer.report_optimized_pick_list').report_action(self)
