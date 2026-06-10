from odoo import models, fields, api


class StockLocationRule(models.Model):
    _name = 'stock.location.rule'
    _description = 'Stock Location Rule'
    _order = 'product_category_id, active desc'

    product_category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        required=True,
        help='Product category to which this rule applies'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Disallowed Location',
        required=True,
        help='Destination location that is NOT allowed for products in the category above'
    )
    action = fields.Selection(
        [
            ('warn', 'Warn'),
            ('block', 'Block'),
        ],
        string='Action',
        default='warn',
        required=True,
        help='Warn: show a confirmation dialog. Block: prevent validation entirely.'
    )
    active = fields.Boolean(
        default=True,
        help='Inactive rules are not applied during validation'
    )
    note = fields.Char(
        string='Note',
        help='Internal note explaining this rule (e.g., compliance reason, date added)'
    )

    _sql_constraints = [
        ('unique_rule', 'UNIQUE(product_category_id, location_id)', 'A rule for this category and location already exists.')
    ]

    def _get_violations(self, move_lines):
        """
        Check if any move lines violate this rule set.
        Returns a list of dicts with violation details.
        """
        violations = []

        for move in move_lines:
            if not move.location_dest_id:
                continue

            # Get all active rules for this product's category
            product_category = move.product_id.categ_id
            if not product_category:
                continue

            matching_rules = self.search([
                ('product_category_id', '=', product_category.id),
                ('location_id', '=', move.location_dest_id.id),
                ('active', '=', True),
            ])

            for rule in matching_rules:
                violations.append({
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'product_name': move.product_id.name,
                    'category_name': product_category.name,
                    'destination_location': move.location_dest_id.name,
                    'rule_id': rule.id,
                    'action': rule.action,
                    'note': rule.note,
                })

        return violations
