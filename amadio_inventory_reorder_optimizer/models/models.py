from odoo import models, fields, api
from datetime import timedelta

class InventoryForecast(models.Model):
    _name = "inventory.forecast"
    _description = "Inventory Forecast"
    _order = "status, avg_daily_demand desc"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    avg_daily_demand = fields.Float(string="Avg Daily Demand", compute="_compute_avg_daily_demand")
    lead_time_days = fields.Integer(string="Lead Time (Days)", default=1)
    safety_stock_days = fields.Integer(string="Safety Stock (Days)", default=7)
    suggested_reorder_point = fields.Float(string="Suggested Reorder Point", compute="_compute_reorder_point")
    suggested_max_qty = fields.Float(string="Suggested Max Qty", compute="_compute_max_qty")
    last_computed_date = fields.Date(string="Last Computed", auto_now=True)
    status = fields.Selection(
        [("healthy", "Healthy"), ("watch", "Watch"), ("critical", "Critical")],
        string="Status",
        compute="_compute_status"
    )

    @api.depends("product_id")
    def _compute_avg_daily_demand(self):
        """Calculate average daily demand from last 12 months"""
        for forecast in self:
            if forecast.product_id:
                past_date = fields.Date.today() - timedelta(days=365)
                moves = self.env["stock.move"].search([
                    ("product_id", "=", forecast.product_id.id),
                    ("date", ">=", past_date),
                    ("state", "=", "done")
                ])
                if moves:
                    total_qty = sum(moves.mapped("quantity_done"))
                    forecast.avg_daily_demand = total_qty / 365
                else:
                    forecast.avg_daily_demand = 0
            else:
                forecast.avg_daily_demand = 0

    @api.depends("avg_daily_demand", "lead_time_days", "safety_stock_days")
    def _compute_reorder_point(self):
        for forecast in self:
            forecast.suggested_reorder_point = (
                forecast.avg_daily_demand * (forecast.lead_time_days + forecast.safety_stock_days)
            )

    @api.depends("avg_daily_demand", "safety_stock_days")
    def _compute_max_qty(self):
        for forecast in self:
            forecast.suggested_max_qty = forecast.avg_daily_demand * 90  # 90 days worth

    @api.depends("status")
    def _compute_status(self):
        for forecast in self:
            stock_level = forecast.product_id.qty_available if forecast.product_id else 0
            if stock_level < forecast.suggested_reorder_point:
                forecast.status = "critical"
            elif stock_level < forecast.suggested_reorder_point * 1.5:
                forecast.status = "watch"
            else:
                forecast.status = "healthy"

    def action_generate_po(self):
        """Generate draft purchase order"""
        self.ensure_one()
        # Implementation for generating POs
        pass

class ProductTemplate(models.Model):
    _inherit = "product.template"

    forecast_id = fields.Many2one("inventory.forecast", string="Forecast", compute="_compute_forecast")
    forecast_status = fields.Selection(
        [("healthy", "Healthy"), ("watch", "Watch"), ("critical", "Critical")],
        string="Forecast Status",
        compute="_compute_forecast_status"
    )

    @api.depends("product_variant_ids")
    def _compute_forecast(self):
        for template in self:
            if template.product_variant_ids:
                template.forecast_id = self.env["inventory.forecast"].search(
                    [("product_id", "=", template.product_variant_ids[0].id)],
                    limit=1
                )

    @api.depends("forecast_id")
    def _compute_forecast_status(self):
        for template in self:
            template.forecast_status = template.forecast_id.status if template.forecast_id else False
