from odoo import models, fields, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class StockExpiryRule(models.Model):
    _name = "stock.expiry.rule"
    _description = "Stock Expiry Alert Rule"

    name = fields.Char(string="Rule Name", required=True)
    product_category_id = fields.Many2one("product.category", string="Product Category")
    product_id = fields.Many2one("product.product", string="Product")
    warn_days_before = fields.Integer(string="Warn Days Before", default=30)
    block_days_before = fields.Integer(string="Block Days Before", default=0)
    alert_partner_ids = fields.Many2many("res.partner", string="Alert Recipients")
    auto_quarantine = fields.Boolean(string="Auto-Quarantine", default=False)
    active = fields.Boolean(string="Active", default=True)

class StockLot(models.Model):
    _inherit = "stock.lot"

    expiry_alert_state = fields.Selection(
        [("ok", "OK"), ("warning", "Warning"), ("critical", "Critical"), ("expired", "Expired")],
        string="Expiry Alert State",
        compute="_compute_expiry_alert_state"
    )
    days_to_expiry = fields.Integer(string="Days to Expiry", compute="_compute_days_to_expiry")
    quarantine_location_id = fields.Many2one("stock.location", string="Quarantine Location")

    @api.depends("expiration_date")
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for lot in self:
            if lot.expiration_date:
                delta = (lot.expiration_date - today).days
                lot.days_to_expiry = delta
            else:
                lot.days_to_expiry = -1

    @api.depends("days_to_expiry")
    def _compute_expiry_alert_state(self):
        for lot in self:
            if lot.days_to_expiry < 0:
                lot.expiry_alert_state = "expired"
            elif lot.days_to_expiry == 0:
                lot.expiry_alert_state = "critical"
            elif lot.days_to_expiry <= 7:
                lot.expiry_alert_state = "warning"
            else:
                lot.expiry_alert_state = "ok"

    def action_quarantine_lot(self):
        """Move lot to quarantine location"""
        self.ensure_one()
        if not self.quarantine_location_id:
            quarantine_loc = self.env["stock.location"].search(
                [("name", "=", "Quarantine")],
                limit=1
            )
            if not quarantine_loc:
                quarantine_loc = self.env["stock.location"].create({
                    "name": "Quarantine",
                    "location_id": self.env.ref("stock.stock_location_locations").id,
                    "usage": "internal",
                })
            self.quarantine_location_id = quarantine_loc
        return True

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        """Check expiry when validating"""
        for line in self:
            if line.lot_id and line.lot_id.expiration_date:
                rule = self.env["stock.expiry.rule"].search(
                    ["|", ("product_id", "=", line.product_id.id),
                     ("product_category_id", "=", line.product_id.categ_id.id)]
                )
                if rule and line.lot_id.days_to_expiry <= rule.block_days_before:
                    raise ValidationError(f"Cannot move expired lot {line.lot_id.name}")
        return super()._action_done()
