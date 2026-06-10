from odoo import models, fields, api
from datetime import timedelta

class HROnboardingTemplate(models.Model):
    _name = "hr.onboarding.template"
    _description = "HR Onboarding Template"

    name = fields.Char(string="Template Name", required=True)
    department_id = fields.Many2one("hr.department", string="Department Filter")
    step_ids = fields.One2many("hr.onboarding.template.step", "template_id", string="Steps")
    active = fields.Boolean(string="Active", default=True)

class HROnboardingTemplateStep(models.Model):
    _name = "hr.onboarding.template.step"
    _description = "Onboarding Template Step"
    _order = "sequence"

    template_id = fields.Many2one("hr.onboarding.template", string="Template", required=True)
    name = fields.Char(string="Step Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    responsible_role = fields.Selection(
        [("hr", "HR"), ("it", "IT"), ("manager", "Manager"), ("employee", "Employee")],
        string="Responsible Role",
        required=True
    )
    is_critical = fields.Boolean(string="Critical Step", default=False)
    due_days_after_start = fields.Integer(string="Days After Start", default=1)
    description = fields.Text(string="Description")

class HROnboardingChecklist(models.Model):
    _name = "hr.onboarding.checklist"
    _description = "HR Onboarding Checklist"
    _order = "start_date desc"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    template_id = fields.Many2one("hr.onboarding.template", string="Template", required=True)
    state = fields.Selection(
        [("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="in_progress"
    )
    start_date = fields.Date(string="Start Date", default=fields.Date.today)
    target_completion_date = fields.Date(string="Target Completion Date")
    completion_pct = fields.Float(string="Completion %", compute="_compute_completion_pct")
    step_ids = fields.One2many("hr.onboarding.step", "checklist_id", string="Steps")

    @api.onchange("template_id")
    def _onchange_template(self):
        if self.template_id:
            self.step_ids = [(5, 0, 0)]
            for template_step in self.template_id.step_ids:
                self.step_ids.append((0, 0, {
                    "name": template_step.name,
                    "responsible_id": False,
                    "is_critical": template_step.is_critical,
                    "due_date": self.start_date + timedelta(days=template_step.due_days_after_start),
                    "notes": template_step.description,
                }))

    @api.depends("step_ids.done")
    def _compute_completion_pct(self):
        for checklist in self:
            if checklist.step_ids:
                done_count = len(checklist.step_ids.filtered("done"))
                checklist.completion_pct = (done_count / len(checklist.step_ids)) * 100
            else:
                checklist.completion_pct = 0

class HROnboardingStep(models.Model):
    _name = "hr.onboarding.step"
    _description = "Onboarding Step"
    _order = "due_date"

    checklist_id = fields.Many2one("hr.onboarding.checklist", string="Checklist", required=True)
    name = fields.Char(string="Step", required=True)
    responsible_id = fields.Many2one("res.users", string="Responsible")
    done = fields.Boolean(string="Done", default=False)
    done_date = fields.Date(string="Done Date")
    is_critical = fields.Boolean(string="Critical", default=False)
    due_date = fields.Date(string="Due Date")
    notes = fields.Text(string="Notes")

class HREmployee(models.Model):
    _inherit = "hr.employee"

    onboarding_checklist_ids = fields.One2many("hr.onboarding.checklist", "employee_id", string="Onboarding Checklists")
    onboarding_count = fields.Integer(string="Onboarding Count", compute="_compute_onboarding_count")

    def _compute_onboarding_count(self):
        for employee in self:
            employee.onboarding_count = len(employee.onboarding_checklist_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-launch default onboarding template on employee creation"""
        employees = super().create(vals_list)
        default_template = self.env["hr.onboarding.template"].search(
            [("active", "=", True)],
            limit=1
        )
        for employee in employees:
            if default_template:
                self.env["hr.onboarding.checklist"].create({
                    "employee_id": employee.id,
                    "template_id": default_template.id,
                })
        return employees
