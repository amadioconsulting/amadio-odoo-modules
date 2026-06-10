from odoo import models, fields, api
from datetime import timedelta

class ContractContract(models.Model):
    _name = "contract.contract"
    _description = "Contract"
    _order = "start_date desc"

    name = fields.Char(string="Contract Name", required=True)
    ref = fields.Char(string="Reference", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Party", required=True)
    contract_type = fields.Selection(
        [("customer", "Customer"), ("vendor", "Vendor"), ("employment", "Employment"),
         ("nda", "NDA"), ("other", "Other")],
        string="Type",
        required=True
    )
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    renewal_notice_days = fields.Integer(string="Renewal Notice Days", default=90)
    auto_renew = fields.Boolean(string="Auto-Renew", default=False)
    value = fields.Float(string="Contract Value")
    currency_id = fields.Many2one("res.currency", string="Currency")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("pending_renewal", "Pending Renewal"),
         ("renewed", "Renewed"), ("expired", "Expired"), ("terminated", "Terminated")],
        string="State",
        default="draft"
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    legal_contact_id = fields.Many2one("res.partner", string="Legal Contact")
    alert_partner_ids = fields.Many2many("res.partner", string="Alert Recipients")
    amendment_ids = fields.One2many("contract.amendment", "contract_id", string="Amendments")
    sale_order_ids = fields.Many2many("sale.order", string="Related Sales Orders")
    days_to_expiry = fields.Integer(string="Days to Expiry", compute="_compute_days_to_expiry")
    renewal_alert_date = fields.Date(string="Renewal Alert Date", compute="_compute_renewal_alert_date")

    @api.depends("end_date")
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for contract in self:
            if contract.end_date:
                contract.days_to_expiry = (contract.end_date - today).days
            else:
                contract.days_to_expiry = -1

    @api.depends("end_date", "renewal_notice_days")
    def _compute_renewal_alert_date(self):
        for contract in self:
            if contract.end_date:
                contract.renewal_alert_date = contract.end_date - timedelta(days=contract.renewal_notice_days)
            else:
                contract.renewal_alert_date = False

    def action_renew(self):
        """Create a new contract linked to original"""
        self.ensure_one()
        new_contract = self.create({
            "name": f"{self.name} (Renewed)",
            "partner_id": self.partner_id.id,
            "contract_type": self.contract_type,
            "start_date": self.end_date + timedelta(days=1),
            "end_date": self.end_date + timedelta(days=365),
            "owner_id": self.owner_id.id,
        })
        self.state = "renewed"
        return new_contract

class ContractAmendment(models.Model):
    _name = "contract.amendment"
    _description = "Contract Amendment"

    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    name = fields.Char(string="Amendment Title", required=True)
    date = fields.Date(string="Date", required=True)
    description = fields.Text(string="Description")
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
