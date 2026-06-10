from odoo import models, fields, api
from datetime import timedelta

class AccountReminderSequence(models.Model):
    _name = "account.reminder.sequence"
    _description = "Invoice Reminder Sequence"

    name = fields.Char(string="Sequence Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    stage_ids = fields.One2many("account.reminder.stage", "sequence_id", string="Stages")

class AccountReminderStage(models.Model):
    _name = "account.reminder.stage"
    _description = "Reminder Stage"
    _order = "days_overdue"

    sequence_id = fields.Many2one("account.reminder.sequence", string="Sequence", required=True)
    name = fields.Char(string="Stage Name", required=True)
    days_overdue = fields.Integer(string="Days Overdue", required=True)
    email_template_id = fields.Many2one("mail.template", string="Email Template")
    send_copy_to_ids = fields.Many2many("res.partner", string="CC Recipients")
    escalate_to_id = fields.Many2one("res.users", string="Escalate To")

class ResPartner(models.Model):
    _inherit = "res.partner"

    reminder_sequence_id = fields.Many2one("account.reminder.sequence", string="Reminder Sequence")
    reminder_paused = fields.Boolean(string="Reminders Paused", default=False)

class AccountMove(models.Model):
    _inherit = "account.move"

    last_reminder_date = fields.Date(string="Last Reminder Date")
    last_reminder_stage_id = fields.Many2one("account.reminder.stage", string="Last Reminder Stage")
    reminder_count = fields.Integer(string="Reminder Count", default=0)
    reminder_log_ids = fields.One2many("account.reminder.log", "move_id", string="Reminder Logs")

class AccountReminderLog(models.Model):
    _name = "account.reminder.log"
    _description = "Reminder Log"
    _order = "sent_date desc"

    move_id = fields.Many2one("account.move", string="Invoice", required=True)
    stage_id = fields.Many2one("account.reminder.stage", string="Stage")
    sent_date = fields.Datetime(string="Sent Date", default=fields.Datetime.now)
    sent_by_id = fields.Many2one("res.users", string="Sent By")
    note = fields.Text(string="Notes")
