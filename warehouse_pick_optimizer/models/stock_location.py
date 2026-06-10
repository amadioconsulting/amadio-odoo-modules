from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    pick_sequence = fields.Integer(
        string='Pick Sequence',
        default=0,
        help='Order for picking operations. Lower numbers are picked first. Used to optimize pick paths by shelf location.'
    )
