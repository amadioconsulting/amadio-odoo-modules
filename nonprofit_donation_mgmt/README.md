# Nonprofit Donation Management

**Version:** 18.0.1.0.0
**Author:** AMADIO
**License:** LGPL-3
**Price:** EUR 149.00
**Category:** Accounting/Accounting

## Overview

Nonprofit Donation Management is a comprehensive Odoo 18.0 module designed to help nonprofits, religious organizations, charities, and faith-based communities manage donations effectively. The module tracks donations from multiple sources, generates professional tax receipts, manages donor relationships, and provides year-end tax documentation.

## Key Features

- **Multi-Method Donation Tracking**: Record donations via cash, cheque, e-transfer, card, or other payment methods
- **Donor Management**: Complete contact records with donation history and preferences
- **Donation Campaigns**: Organize fundraising campaigns with start/end dates and progress tracking
- **Fund Management**: Track donations by restricted funds or purposes
- **Tax Receipt Generation**: Professional PDF receipts in Canadian T4A-ready format
- **Year-End Statements**: Generate comprehensive donor summaries for tax documentation
- **Accounting Integration**: Optional automatic journal entry creation for GL tracking
- **Donation Workflows**: Draft → Confirmed → Receipted state management
- **Search & Filtering**: Find donations by donor, date, fund, campaign, or payment method
- **Dashboard Views**: Quick overview with Kanban, tree, form, and pivot views

## Who Needs It

- Churches, synagogues, mosques, temples, and religious organizations
- Nonprofits and charitable foundations
- Community service organizations
- Schools and educational charities
- Health and wellness nonprofits
- Environmental and conservation groups
- Artistic and cultural organizations
- Any organization collecting regular donations requiring tax receipts

## Technical Details

### Models

#### donation.donation
Tracks individual donations with:
- Donor (many2one res.partner)
- Date, Amount, Currency
- Payment method (cash/cheque/etransfer/card/other)
- Cheque number tracking
- Fund and campaign assignment
- State workflow (draft/confirmed/receipted)
- Receipt number generation
- Optional GL account posting
- Full audit trail with message thread

#### donation.fund
Manages restricted funds/purposes:
- Fund name and code
- GL account mapping
- Description
- Active/inactive toggle
- Computed totals (donations raised, donation count)

#### donation.campaign
Tracks fundraising campaigns:
- Campaign name and dates
- Fundraising goal
- Fund association
- Progress tracking (percentage toward goal)
- Active period detection
- Computed metrics (total raised, donation count)

#### donation.year_end_wizard
Transient model for generating year-end statements:
- Select donor and tax year
- Auto-calculate totals
- Generate PDF statement report

### Views

All models include:
- **Tree View**: Columnar list with sorting/grouping
- **Form View**: Detailed entry with workflow buttons
- **Search View**: Advanced filtering and grouping
- **Kanban View**: (Donation only) State-based card layout
- **Pivot View**: (Donation only) Analytical cross-tabulation

### Reports

#### Donation Receipt
Professional PDF receipt showing:
- Organization name/logo/contact
- Receipt and reference numbers
- Date
- Donor information (name and address)
- Amount in figures
- Fund/purpose
- Payment method
- Tax deduction notice
- Signature line for authorized representative
- CRA compliance statement

#### Year-End Donation Statement
Comprehensive annual summary including:
- All donations for donor in selected year
- Detailed donation table (date, reference, fund, amount)
- Total donations summary
- Tax year notation
- CRA-compliant language

### Workflow States

1. **Draft**: Initial state, can edit all fields, can set to draft
2. **Confirmed**: Validated donation, can generate receipt or post to accounting
3. **Receipted**: Receipt generated and assigned, can print receipt or view GL entry

### Accounting Integration

- Optional GL account posting
- Requires journal selection (bank/cash/general)
- Creates double-entry (debit bank, credit donation revenue)
- Fund can specify GL account for revenue
- Links donation to accounting.move via move_id

## Installation

1. Copy module to Odoo addons directory
2. Update app list
3. Search for "Nonprofit Donation Management"
4. Click Install

## Configuration

### Initial Setup

1. Create Donation Funds (Donations > Funds)
   - Name, code, description
   - Optionally link to GL account for accounting

2. Create Donation Campaigns (Donations > Campaigns)
   - Name, start/end dates, fundraising goal
   - Link to fund

3. Configure Chart of Accounts (if using GL posting)
   - Create donation revenue account
   - Link to funds for automatic posting

### User Permissions

- System users have full access
- Regular users can view/create/edit donations
- Access controlled via ir.model.access.csv

## Usage

### Recording a Donation

1. Go to Donations menu
2. Click Create
3. Fill in donor, date, amount, payment method
4. Optionally select fund and campaign
5. Add notes if needed
6. Save (state = Draft)

### Confirming a Donation

1. Open donation in Draft state
2. Click "Confirm" button
3. Validates donor, amount, and other required fields
4. Sets state to Confirmed

### Generating Receipt

1. Open confirmed donation
2. Click "Generate Receipt" button
3. Receipt number auto-generated
4. State set to Receipted
5. PDF opens for review/printing

### Posting to Accounting

1. Ensure donation is Confirmed or Receipted
2. Select journal (bank/cash account)
3. Fund should have GL account mapped
4. Click "Post to Accounting" button
5. Creates journal entry in GL
6. Links to donation via move_id

### Year-End Reports

1. Go to Donations > Reports > Year-End Statements
2. Select donor and tax year
3. System calculates total donations
4. Click "Generate PDF Statement"
5. Downloads professional year-end document

## Database Schema

### donation.donation
- id (primary key)
- donor_id (FK to res.partner)
- date (date)
- amount (numeric)
- currency_id (FK to res.currency)
- payment_method (selection)
- cheque_number (char)
- fund_id (FK to donation.fund)
- campaign_id (FK to donation.campaign)
- reference (char, unique)
- receipt_number (char, unique)
- state (selection)
- note (text)
- journal_id (FK to account.journal)
- move_id (FK to account.move)
- create_date, write_date (audit)
- create_uid, write_uid (audit)

### donation.fund
- id (primary key)
- name (char, required)
- code (char)
- description (text)
- account_id (FK to account.account)
- active (boolean)

### donation.campaign
- id (primary key)
- name (char, required)
- date_start (date)
- date_end (date)
- goal_amount (numeric)
- fund_id (FK to donation.fund)
- description (text)
- active (boolean)
- currency_id (FK to res.currency)

## Security & Data Protection

- Full row-level access control via groups
- Donation records inherit company context
- Accounting entries require account module permissions
- Audit trail maintained for all changes
- Message threading for collaboration

## Dependencies

- **account**: For GL posting and journal management
- **mail**: For message threads and activity tracking
- Standard Odoo 18.0 modules (base, web, etc.)

## Customization

The module is highly extensible:
- Add custom fields to donation.donation
- Extend reports with custom QWeb templates
- Create additional workflows via state selection
- Hook into action_confirm, action_generate_receipt for custom logic
- Add computed fields for analytics

## Support & Troubleshooting

### Donation won't confirm
- Ensure donor is selected
- Ensure amount > 0
- Check that all required fields are filled

### Receipt not generating
- Ensure donation is in Confirmed or Receipted state
- Verify company has proper name/address for receipt
- Check browser permissions for PDF download

### GL posting fails
- Ensure journal is selected
- Verify journal has default account
- Check that fund has GL account linked
- Ensure account module is installed

### Year-end report empty
- Verify donations are in Receipted state
- Check that dates fall within selected year
- Ensure donor is selected

## License

LGPL-3 (GNU Lesser General Public License v3)

## Author

AMADIO
https://amadio.io

## Changelog

### v18.0.1.0.0 (Initial Release)
- Complete donation management system
- Tax receipt generation (Canadian T4A format)
- Year-end reporting
- GL accounting integration
- Multi-language support ready
- Full Odoo 18.0 compatibility

---

**Thank you for supporting nonprofits and charities with AMADIO's Nonprofit Donation Management!**
