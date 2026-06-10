from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseApprovalTier(models.Model):
    _name = "purchase.approval.tier"
    _description = "Purchase Approval Tier"
    _order = "sequence"

    name = fields.Char(string="Tier Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    min_amount = fields.Float(string="Minimum Amount", required=True)
    max_amount = fields.Float(string="Maximum Amount")
    approver_ids = fields.Many2many("res.users", string="Approvers")
    require_all = fields.Boolean(string="Require All Approvals", default=False)

    @api.constrains("min_amount", "max_amount")
    def _check_amounts(self):
        for record in self:
            if record.max_amount and record.max_amount < record.min_amount:
                raise ValidationError("Maximum amount must be >= minimum amount")

class PurchaseApprovalLog(models.Model):
    _name = "purchase.approval.log"
    _description = "Purchase Approval Log"
    _order = "date desc"

    order_id = fields.Many2one("purchase.order", string="Purchase Order", required=True)
    approver_id = fields.Many2one("res.users", string="Approver", required=True)
    action = fields.Selection(
        [("approve", "Approved"), ("reject", "Rejected"), ("reset", "Reset")],
        string="Action",
        required=True
    )
    note = fields.Text(string="Notes")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval_tier_id = fields.Many2one("purchase.approval.tier", string="Approval Tier", compute="_compute_approval_tier")
    approval_state = fields.Selection(
        [("pending_approval", "Pending Approval"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="Approval State",
        default="pending_approval"
    )
    approval_log_ids = fields.One2many("purchase.approval.log", "order_id", string="Approval Logs")
    current_approver_ids = fields.Many2many("res.users", string="Current Approvers", compute="_compute_current_approvers")

    @api.depends("amount_total")
    def _compute_approval_tier(self):
        for order in self:
            tier = self.env["purchase.approval.tier"].search(
                [("min_amount", "<=", order.amount_total),
                 "|", ("max_amount", "=", False), ("max_amount", ">=", order.amount_total)],
                order="min_amount desc",
                limit=1
            )
            order.approval_tier_id = tier

    @api.depends("approval_tier_id")
    def _compute_current_approvers(self):
        for order in self:
            order.current_approver_ids = order.approval_tier_id.approver_ids if order.approval_tier_id else False

    def button_confirm(self):
        """Override confirm to check approval tier"""
        for order in self:
            if order.approval_tier_id and order.approval_state != "approved":
                raise ValidationError(f"PO must be approved before confirmation. Current approvers: {order.current_approver_ids.mapped('name')}")
        return super().button_confirm()

    def action_approve(self):
        """Approve the purchase order"""
        self.ensure_one()
        self.approval_state = "approved"
        self.approval_log_ids.create({
            "order_id": self.id,
            "approver_id": self.env.user.id,
            "action": "approve"
        })

    def action_reject(self):
        """Reject the purchase order"""
        self.ensure_one()
        self.approval_state = "rejected"
        self.approval_log_ids.create({
            "order_id": self.id,
            "approver_id": self.env.user.id,
            "action": "reject"
        })
