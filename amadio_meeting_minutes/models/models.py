from odoo import models, fields, api

class MeetingMinutes(models.Model):
    _name = "meeting.minutes"
    _description = "Meeting Minutes"
    _order = "date desc"

    event_id = fields.Many2one("calendar.event", string="Event")
    title = fields.Char(string="Title", compute="_compute_title")
    date = fields.Date(string="Date", required=True)
    facilitator_id = fields.Many2one("res.users", string="Facilitator")
    attendee_ids = fields.Many2many("res.partner", string="Attendees")
    agenda = fields.Text(string="Agenda")
    decisions = fields.Text(string="Decisions")
    summary = fields.Text(string="Summary")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published")],
        string="State",
        default="draft"
    )
    action_item_ids = fields.One2many("meeting.action.item", "minutes_id", string="Action Items")

    @api.depends("event_id")
    def _compute_title(self):
        for minutes in self:
            minutes.title = minutes.event_id.name if minutes.event_id else "Meeting Minutes"

    def action_publish(self):
        """Publish minutes and send email"""
        self.ensure_one()
        self.state = "published"

class MeetingActionItem(models.Model):
    _name = "meeting.action.item"
    _description = "Meeting Action Item"
    _order = "due_date, priority"

    minutes_id = fields.Many2one("meeting.minutes", string="Minutes", required=True)
    description = fields.Char(string="Description", required=True)
    owner_id = fields.Many2one("res.users", string="Owner")
    due_date = fields.Date(string="Due Date")
    done = fields.Boolean(string="Done", default=False)
    done_date = fields.Date(string="Done Date")
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Priority",
        default="medium"
    )

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    minutes_id = fields.Many2one("meeting.minutes", string="Minutes")
    minutes_count = fields.Integer(string="Minutes Count", compute="_compute_minutes_count")

    def _compute_minutes_count(self):
        for event in self:
            event.minutes_count = self.env["meeting.minutes"].search_count([("event_id", "=", event.id)])
