from odoo import models, fields, api
from datetime import datetime, timedelta

class CommissionPlan(models.Model):
    _name = "commission.plan"
    _description = "Commission Plan"

    name = fields.Char(string="Plan Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    rule_ids = fields.One2many("commission.rule", "plan_id", string="Rules")

class CommissionRule(models.Model):
    _name = "commission.rule"
    _description = "Commission Rule"

    plan_id = fields.Many2one("commission.plan", string="Plan", required=True)
    name = fields.Char(string="Rule Name", required=True)
    commission_type = fields.Selection(
        [("pct", "Percentage"), ("fixed", "Fixed Amount")],
        string="Type",
        required=True
    )
    rate = fields.Float(string="Rate/Amount", required=True)
    product_category_id = fields.Many2one("product.category", string="Product Category")
    min_amount = fields.Float(string="Minimum Amount")
    based_on = fields.Selection(
        [("invoiced", "Invoiced"), ("paid", "Paid")],
        string="Based On",
        default="invoiced"
    )

class ResUsers(models.Model):
    _inherit = "res.users"

    commission_plan_id = fields.Many2one("commission.plan", string="Commission Plan")

class CommissionStatement(models.Model):
    _name = "commission.statement"
    _description = "Commission Statement"
    _order = "period_start desc"

    user_id = fields.Many2one("res.users", string="User", required=True)
    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("paid", "Paid")],
        string="State",
        default="draft"
    )
    line_ids = fields.One2many("commission.statement.line", "statement_id", string="Lines")
    total_commission = fields.Float(string="Total Commission", compute="_compute_total")

    @api.depends("line_ids.commission_amount")
    def _compute_total(self):
        for statement in self:
            statement.total_commission = sum(statement.line_ids.mapped("commission_amount"))

    def action_submit(self):
        self.ensure_one()
        self.state = "submitted"

    def action_approve(self):
        self.ensure_one()
        self.state = "approved"

    def action_mark_paid(self):
        self.ensure_one()
        self.state = "paid"

class CommissionStatementLine(models.Model):
    _name = "commission.statement.line"
    _description = "Commission Statement Line"

    statement_id = fields.Many2one("commission.statement", string="Statement", required=True)
    invoice_id = fields.Many2one("account.move", string="Invoice")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
    base_amount = fields.Float(string="Base Amount", required=True)
    rate = fields.Float(string="Commission Rate", required=True)
    commission_amount = fields.Float(string="Commission Amount", compute="_compute_commission")

    @api.depends("base_amount", "rate")
    def _compute_commission(self):
        for line in self:
            line.commission_amount = (line.base_amount * line.rate) / 100
