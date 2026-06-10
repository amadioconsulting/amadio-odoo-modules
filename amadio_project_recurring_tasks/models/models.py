from odoo import models, fields, api
from datetime import datetime, timedelta

class ProjectTaskRecurrenceTemplate(models.Model):
    _name = "project.task.recurrence.template"
    _description = "Task Recurrence Template"

    name = fields.Char(string="Template Name", required=True)
    project_id = fields.Many2one("project.project", string="Project", required=True)
    stage_id = fields.Many2one("project.task.type", string="Default Stage")
    user_ids = fields.Many2many("res.users", string="Assigned Users")
    tag_ids = fields.Many2many("project.tags", string="Tags")
    description = fields.Text(string="Description")
    recurrence_type = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("custom", "Custom")],
        string="Recurrence Type",
        default="monthly"
    )
    day_of_week = fields.Selection(
        [(str(i), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]) for i in range(7)],
        string="Day of Week"
    )
    day_of_month = fields.Integer(string="Day of Month")
    interval = fields.Integer(string="Interval", default=1)
    custom_cron = fields.Char(string="Custom Cron Expression")
    next_run_date = fields.Date(string="Next Run Date", compute="_compute_next_run")
    active = fields.Boolean(string="Active", default=True)

    @api.depends("recurrence_type", "day_of_week", "day_of_month")
    def _compute_next_run(self):
        today = fields.Date.today()
        for template in self:
            if template.recurrence_type == "daily":
                template.next_run_date = today
            elif template.recurrence_type == "weekly":
                template.next_run_date = today
            elif template.recurrence_type == "monthly":
                template.next_run_date = today
            else:
                template.next_run_date = today

class ProjectTask(models.Model):
    _inherit = "project.task"

    recurrence_template_id = fields.Many2one("project.task.recurrence.template", string="Recurrence Template")
