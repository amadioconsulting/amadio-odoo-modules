from odoo import models, fields, api

class AssetMaintenanceSchedule(models.Model):
    _name = "asset.maintenance.schedule"
    _description = "Asset Maintenance Schedule"

    asset_id = fields.Many2one("account.asset", string="Asset", required=True)
    name = fields.Char(string="Schedule Name", required=True)
    schedule_type = fields.Selection(
        [("time", "Time"), ("usage", "Usage")],
        string="Type",
        required=True
    )
    interval_days = fields.Integer(string="Interval (Days)")
    interval_count = fields.Integer(string="Interval Count")
    last_maintenance_date = fields.Date(string="Last Maintenance Date")
    next_maintenance_date = fields.Date(string="Next Maintenance Date", compute="_compute_next_maintenance")
    responsible_id = fields.Many2one("res.users", string="Responsible")
    alert_days_before = fields.Integer(string="Alert Days Before", default=7)
    alert_partner_ids = fields.Many2many("res.partner", string="Alert Recipients")
    active = fields.Boolean(string="Active", default=True)

    @api.depends("last_maintenance_date", "interval_days")
    def _compute_next_maintenance(self):
        from datetime import timedelta
        for schedule in self:
            if schedule.last_maintenance_date and schedule.interval_days:
                schedule.next_maintenance_date = schedule.last_maintenance_date + timedelta(days=schedule.interval_days)
            else:
                schedule.next_maintenance_date = False

class AssetMaintenanceLog(models.Model):
    _name = "asset.maintenance.log"
    _description = "Maintenance Log"
    _order = "date desc"

    schedule_id = fields.Many2one("asset.maintenance.schedule", string="Schedule", required=True)
    date = fields.Date(string="Date", required=True)
    performed_by_id = fields.Many2one("res.users", string="Performed By")
    cost = fields.Float(string="Cost")
    notes = fields.Text(string="Notes")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")

class AccountAsset(models.Model):
    _inherit = "account.asset"

    maintenance_schedule_ids = fields.One2many("asset.maintenance.schedule", "asset_id", string="Maintenance Schedules")
    maintenance_count = fields.Integer(string="Maintenance Count", compute="_compute_maintenance_count")
    next_maintenance_date = fields.Date(string="Next Maintenance Date", compute="_compute_next_maintenance")

    def _compute_maintenance_count(self):
        for asset in self:
            asset.maintenance_count = len(asset.maintenance_schedule_ids)

    @api.depends("maintenance_schedule_ids.next_maintenance_date")
    def _compute_next_maintenance(self):
        for asset in self:
            dates = asset.maintenance_schedule_ids.mapped("next_maintenance_date").filtered(bool)
            asset.next_maintenance_date = min(dates) if dates else False
