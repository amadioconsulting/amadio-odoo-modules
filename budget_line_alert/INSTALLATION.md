# Analytic Budget Alert & Variance Monitor - Installation & Configuration Guide

## Installation

1. **Copy the module** to your Odoo addons directory:
   ```
   cp -r budget_line_alert /path/to/odoo/addons/
   ```

2. **Update the Odoo app list** and search for "Analytic Budget Alert & Variance Monitor"

3. **Install the module** by clicking the Install button

## Module Overview

**Technical Name:** `budget_line_alert`  
**Version:** 18.0.1.0.0  
**Dependencies:** analytic, account, mail  
**Author:** AMADIO  
**Price:** EUR 59.00

## Features

### Budget Configuration
- Enable/disable budget control per analytic account
- Set budget amounts with company currency
- Choose budget periods: Monthly, Quarterly, Annual, or Custom date ranges
- Configure warn and block thresholds (percentages)

### Alert System
- Email alerts when spending reaches warn threshold
- Prevents posting when spending would exceed block threshold
- Multiple alert recipients per analytic account
- Daily alert deduplication (only one alert per day per account)

### Real-time Monitoring
- Computed fields show:
  - Amount Spent (sum of credits - debits in current period)
  - Budget Remaining
  - Percent Spent (visual progress bar)
- Current period dates calculated automatically based on budget_period setting

### Access Control
- Account users: read-only access to budgets
- Account managers: full access to configure budgets and alert recipients

## Usage Workflow

### Step 1: Enable Budget on an Analytic Account
1. Open Accounting > Analytic Accounts
2. Select an analytic account
3. Go to the "Budget Alert" tab
4. Check "Enable Budget Control"

### Step 2: Configure Budget Parameters
1. Set "Budget Amount" (e.g., 10,000 EUR)
2. Select "Budget Period" (Month/Quarter/Year/Custom)
3. If custom, set "Budget Period From" and "Budget Period To"
4. Set "Warn Threshold %" (e.g., 80%)
5. Set "Block Threshold %" (e.g., 100%)
6. Add alert recipient partners in "Alert Recipients"

### Step 3: Monitor Spending
When vendor bills or expenses are posted with this analytic account:
- System automatically calculates spending in current period
- If spending > warn threshold: Email alert sent to recipients
- If spending would exceed block threshold: Posting prevented with error

### Step 4: View Budget Status
- Open the analytic account form to see real-time budget status
- Progress bar shows percent spent visually
- "Amount Spent" shows current period total
- "Budget Remaining" shows available budget

## Configuration Examples

### Monthly Project Budget
- Budget Amount: 25,000 EUR
- Budget Period: Monthly
- Warn Threshold: 80%
- Block Threshold: 100%
- Alert Recipients: Project Manager, Finance Lead

### Grant-Funded Project
- Budget Amount: 50,000 EUR
- Budget Period: Custom (2026-01-01 to 2026-12-31)
- Warn Threshold: 75% (grant has tight requirements)
- Block Threshold: 95% (buffer for last-minute expenses)
- Alert Recipients: Finance, Grant Coordinator, Donor Relations

### Ministry Department Budget
- Budget Amount: 5,000 EUR
- Budget Period: Monthly
- Warn Threshold: 90% (flexible)
- Block Threshold: 110% (allows minor overages)
- Alert Recipients: Ministry Director

## Technical Details

### Database Changes
Creates/modifies these fields on `account.analytic.account`:
- budget_enabled (Boolean)
- budget_amount (Monetary)
- budget_period (Selection)
- budget_date_from (Date)
- budget_date_to (Date)
- budget_warn_pct (Float)
- budget_block_pct (Float)
- budget_alert_partner_ids (Many2many)
- budget_spent (Computed Monetary)
- budget_remaining (Computed Monetary)
- budget_pct_spent (Computed Float)
- budget_last_alert_date (Date)

### Inherits
- account.analytic.account (adds budget fields and methods)
- account.move.line (adds budget checking on posting)

### Key Methods
- `_get_period_dates()` - Calculate period start/end dates
- `_send_budget_alert()` - Send email to alert recipients
- `_compute_budget_spent()` - Calculate amount spent in period
- `_compute_budget_remaining()` - Calculate remaining budget
- `_compute_budget_pct_spent()` - Calculate percent spent
- `_check_analytic_budget()` - Validate against thresholds
- `_check_budget_on_line()` - Check budget for account move line

## Security & Permissions

- **account.group_account_user**: Read access to budget fields
- **account.group_account_manager**: Full access to budget configuration

## Troubleshooting

### Alerts Not Sending
1. Verify alert recipients have valid email addresses
2. Check mail outgoing server configuration in Odoo
3. Verify budget_enabled is checked on the account
4. Ensure amount exceeds warn threshold

### Budget Check Not Blocking
1. Verify block threshold is set below 100% if you want to block before full budget
2. Check that budget_enabled is True
3. Ensure the analytic account is properly linked to the journal entry
4. Verify budget period is correct (spending outside period won't count)

### Percent Spent Shows 0%
1. Check that budget_amount is set and > 0
2. Verify budget_period is correctly configured
3. Ensure analytic lines exist in current period
4. Check that analytic lines have proper credit/debit values

## Support

For issues, feature requests, or support:
- Email: support@amadio.io
- Website: https://amadio.io
