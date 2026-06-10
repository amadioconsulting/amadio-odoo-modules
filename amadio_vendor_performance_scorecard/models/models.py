from odoo import models, fields, api

class VendorScorecard(models.Model):
    _name = "vendor.scorecard"
    _description = "Vendor Performance Scorecard"
    _order = "period desc"

    partner_id = fields.Many2one("res.partner", string="Vendor", required=True)
    period = fields.Char(string="Period", required=True)
    overall_score = fields.Float(string="Overall Score", compute="_compute_overall_score")
    delivery_score = fields.Float(string="Delivery Score")
    quality_score = fields.Float(string="Quality Score")
    price_score = fields.Float(string="Price Score")
    service_score = fields.Float(string="Service Score")
    notes = fields.Text(string="Notes")

    @api.depends("delivery_score", "quality_score", "price_score", "service_score")
    def _compute_overall_score(self):
        for scorecard in self:
            scores = [scorecard.delivery_score, scorecard.quality_score,
                     scorecard.price_score, scorecard.service_score]
            scorecard.overall_score = sum(scores) / len([s for s in scores if s]) if any(scores) else 0

class VendorScorecardCriterion(models.Model):
    _name = "vendor.scorecard.criterion"
    _description = "Scorecard Criterion"

    name = fields.Char(string="Criterion Name", required=True)
    weight = fields.Float(string="Weight", default=1.0)
    score_type = fields.Selection([("auto", "Automatic"), ("manual", "Manual")], default="auto")

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    quality_rating = fields.Float(string="Quality Rating", digits=(2, 1))
    delivery_rating = fields.Float(string="Delivery Rating", digits=(2, 1))
    price_rating = fields.Float(string="Price Rating", digits=(2, 1))
    service_rating = fields.Float(string="Service Rating", digits=(2, 1))
    rating_notes = fields.Text(string="Rating Notes")
