# Analytic Budget Alert & Variance Monitor

**Technical Name:** `budget_line_alert`
**Version:** 18.0.1.0.0
**Author:** AMADIO (https://amadio.io)
**Price:** EUR 59.00

## Overview

A professional Odoo 18.0 accounting module that enables organizations to set spending thresholds on analytic accounts and receive real-time email alerts when budgets are approached. The system can automatically prevent posting of transactions that would exceed a configured block threshold.

Perfect for nonprofits, project-based organizations, churches, ministries, and SMBs that need granular budget control without slowing down the approval process.

## Key Features

### Budget Control Per Analytic Account
- Enable/disable budgets individually per account
- Set budget amounts with automatic currency handling
- Choose from monthly, quarterly, annual, or custom date range periods

### Intelligent Threshold System
- **Warn Threshold (%)**: Trigger email alerts when this percentage is reached
- **Block Threshold (%)**: Prevent posting when this percentage would be exceeded
- Constraints ensure warn % ≤ block %

### Real-time Email Alerts
- Automatic notifications to configured recipients
- Only one alert per analytic account per day (deduplication)
- Email includes budget status, percent spent, and period details

### Visual Budget Tracking
- Progress bar showing percent spent on account form
- Computed fields for amount spent, remaining budget, and percent spent
- Current period dates automatically calculated

### Multiple Budget Periods
- **Monthly**: Jan 1 - Jan 31, Feb 1 - Feb 28, etc.
- **Quarterly**: Q1 (Jan-Mar), Q2 (Apr-Jun), etc.
- **Annual**: Full calendar year
- **Custom**: Exact date range (e.g., grant period)

### Smart Budget Checking
- Checks budgets when vendor bills or expenses are posted
- Works with analytic distributions (multi-account allocations)
- Respects account move line balance calculations
- Only counts spending in current budget period

## Module Contents

### Files
```
budget_line_alert/
├── __manifest__.py              # Module metadata and configuration
├── __init__.py                  # Package initialization
├── models/
│   ├── __init__.py              # Model imports
│   ├── analytic_account.py       # Budget fields and methods
│   └── account_move_line.py      # Budget checking on posting
├── views/
│   └── analytic_account_views.xml # UI for budget configuration
├── security/
│   └── ir.model.access.csv       # Access control for users/managers
├── static/
│   └── description/
│       ├── icon.png              # Professional module icon (256x256)
│       └── index.html            # Marketing page with features & FAQ
├── INSTALLATION.md               # Installation and configuration guide
├── README.md                     # This file
└── data/                         # Empty (ready for sample data)
```

### Core Models

**account.analytic.account** (inherited)
- Budget configuration fields
- Computed fields for budget status
- Methods for period calculation and alert sending

**account.move.line** (inherited)
- Budget checking on move posting
- Prevents posting if block threshold exceeded
- Triggers warn alerts if threshold reached

## Installation

1. Copy the module to your Odoo addons directory
2. Update the Odoo module list (Settings > Updates > Update Apps List)
3. Search for "Analytic Budget Alert"
4. Click Install

**Dependencies:** analytic, account, mail (all standard Odoo modules)

## Quick Start

1. Go to Accounting > Analytic Accounts
2. Open an analytic account
3. Click the "Budget Alert" tab
4. Check "Enable Budget Control"
5. Set:
   - Budget Amount: e.g., 10,000 EUR
   - Budget Period: Monthly
   - Warn Threshold: 80%
   - Block Threshold: 100%
   - Alert Recipients: Choose partner(s) to email
6. Save

That's it! The system will now:
- Calculate spending in the current month automatically
- Send email alerts when spending reaches 8,000 EUR (80%)
- Block any posting that would exceed 10,000 EUR (100%)

## Features in Detail

### Budget Period Calculation
The system automatically calculates the current period:
- **Monthly**: Today's month (e.g., March 1-31, 2026)
- **Quarterly**: Current quarter (Q1: Jan-Mar, Q2: Apr-Jun, etc.)
- **Annual**: Current year (Jan 1 - Dec 31)
- **Custom**: Your specified date range (Jan 1 - Dec 31, 2026)

Spending is summed from all analytic lines (account.analytic.line) posted in the current period.

### Email Alerts
When a transaction is posted that reaches the warn threshold:
1. System calculates would-be percent spent
2. Compares to budget_warn_pct
3. If exceeded, calls _send_budget_alert()
4. Email sent to all budget_alert_partner_ids
5. Last alert date updated (prevents duplicate daily alerts)

### Posting Block
When posting a transaction that would exceed the block threshold:
1. System raises UserError with detailed message
2. Shows current spend, block threshold, would-be percent
3. User must either:
   - Adjust the transaction amount
   - Increase the budget
   - Disable budget control

### Computed Fields
All budget status fields recalculate in real-time:

**budget_spent**
```python
SUM(credit - debit) on account.analytic.line
WHERE account_id = this account
  AND date >= period_start
  AND date <= period_end
```

**budget_remaining**
```python
budget_amount - budget_spent
```

**budget_pct_spent**
```python
(budget_spent / budget_amount) * 100
```

## Security & Access Control

**account.group_account_user** (reads)
- Can view analytic accounts and budget status
- Cannot modify budget settings

**account.group_account_manager** (full)
- Can configure budgets, thresholds, and alerts
- Can enable/disable budget control

## Use Cases

### Nonprofits
Control spending on grant-funded projects. Set custom periods matching grant cycles and tight thresholds (75%) for compliance.

### Project Organizations
Track project budgets across multiple analytic accounts. Set monthly budgets and get alerts when approaching limits.

### Churches & Ministries
Control departmental spending. Set budgets for each ministry and restrict overspending on dedicated funds.

### SMBs
Manage internal project allocations. Set budgets for R&D, marketing, or internal projects without slowing approvals.

### Cost Centers
Track department spending. Set annual budgets by cost center with monthly alerts.

## Technical Highlights

### Odoo 18 Best Practices
- Uses @api.depends for computed field dependencies
- @api.constrains for validation
- api.model_create_multi for batch operations
- Proper inheritance with _inherit
- Company currency handling
- Monetary field with proper currency_field

### Email Integration
- Uses mail.mail model for reliable delivery
- Respects company email and user email settings
- HTML body formatting
- Proper sender identification

### Budget Calculation
- Handles analytic distributions (%)
- Respects move state transitions
- Works with all account move types
- Proper datetime handling with dateutil
- Period calculation with relativedelta

### Safety & Constraints
- Cannot set warn % > block %
- Custom periods require both from/to dates
- From date must be before to date
- Budget field is ignored if budget_enabled = False
- Budget checks only when move state = 'posted'

## Configuration Examples

### Monthly Department Budget
```
Budget Amount: 5,000 EUR
Period: Monthly
Warn %: 80% (alert at 4,000)
Block %: 100% (block at 5,000)
Alert Recipients: Manager, Finance Lead
```

### Grant-Funded Research
```
Budget Amount: 100,000 EUR
Period: Custom (2026-01-01 to 2026-12-31)
Warn %: 75% (alert at 75,000 - strict grant requirements)
Block %: 95% (block at 95,000 - buffer for final expenses)
Alert Recipients: Finance, Grant Coordinator, PI
```

### Ministry Spending
```
Budget Amount: 2,000 EUR
Period: Monthly
Warn %: 90% (flexible, alert at 1,800)
Block %: 110% (allow minor overages to 2,200)
Alert Recipients: Director, Treasurer
```

## Troubleshooting

**Alerts not sending?**
- Verify alert recipients have email addresses
- Check mail server config (Settings > Outgoing Mail Servers)
- Verify budget_enabled = True
- Check that spending actually exceeds warn %

**Budget check not blocking?**
- Verify block threshold < 100% if you want to block before full budget
- Check budget_enabled = True
- Confirm analytic account linked to journal entry
- Verify budget period is correct

**Percent spent = 0%?**
- Ensure budget_amount > 0
- Verify budget_period configured correctly
- Check analytic lines exist in current period
- Confirm analytic lines have credit/debit values

## Limitations & Notes

- Budget checks only apply when move state = 'posted'
- Already-posted entries are not affected by new budget settings
- Spending is calculated from account.analytic.line credits/debits
- Only one alert per account per calendar day (deduplication)
- Custom periods use exact dates (not relative to fiscal year)

## Support

**Email:** support@amadio.io
**Website:** https://amadio.io

## License

LGPL-3.0 or later (Open source)

## Credits

Built by AMADIO for organizations that need professional budget control.

---

**Version:** 18.0.1.0.0
**Last Updated:** March 30, 2026
**Odoo Compatibility:** 18.0
