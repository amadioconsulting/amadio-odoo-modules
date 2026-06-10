# Installation & Quick Start Guide

## Pre-Installation Checklist

- Odoo 18.0+ installed
- Python 3.8+
- Account module available
- Mail module available
- Database with write permissions

## Installation Steps

### 1. Copy Module to Addons

```bash
cp -r nonprofit_donation_mgmt /path/to/odoo/addons/
```

### 2. Update App List

In Odoo:
- Activate Developer Mode (if not already active)
- Go to Apps > Update Apps List
- Wait for update to complete

### 3. Install Module

- Search for "Nonprofit Donation Management" in Apps
- Click Install
- Wait for installation to complete
- Verify no errors in console

### 4. Verify Installation

Check that these appear in your menu:
- Donations (main menu)
  - Donations (submenu)
  - Funds (submenu)
  - Campaigns (submenu)
  - Reports (submenu)
    - Year-End Statements

## Initial Configuration

### Step 1: Create Donation Funds

1. Go to **Donations > Funds**
2. Click **Create**
3. Fill in:
   - **Fund Name**: e.g., "General Fund", "Building Fund", "Scholarship Fund"
   - **Code**: e.g., "GEN", "BLD", "SCH" (optional)
   - **Description**: Purpose of the fund
   - **GL Account**: (Optional) Link to a revenue account for auto-posting
4. Click **Save**
5. Repeat for each donation fund

### Step 2: Create Donation Campaigns (Optional)

1. Go to **Donations > Campaigns**
2. Click **Create**
3. Fill in:
   - **Campaign Name**: e.g., "Year-End Appeal 2024"
   - **Start Date**: Campaign launch date
   - **End Date**: Campaign completion date
   - **Fundraising Goal**: Target amount (e.g., 10000.00)
   - **Fund**: Link to a fund (or create new)
   - **Description**: Campaign details
4. Click **Save**

### Step 3: Configure Accounting (If Using GL Posting)

1. Go to **Accounting > Chart of Accounts**
2. Create/identify these accounts:
   - **Asset Account**: Bank or Cash (for receiving donations)
   - **Revenue Account**: Donations Income (linked to funds)
3. Go back to **Donations > Funds**
4. Edit each fund
5. Set **GL Account** to appropriate revenue account
6. Save

### Step 4: Configure Journal for Posting

1. Go to **Accounting > Configuration > Journals**
2. Verify your bank/cash journal exists
3. Ensure it has a default account set
4. Note the journal name for donations

## First Donation Entry

1. Go to **Donations > Donations**
2. Click **Create**
3. Fill in:
   - **Donor**: Select or create donor (from res.partner)
   - **Date**: Today's date (or donation date)
   - **Amount**: Donation amount (e.g., 150.00)
   - **Currency**: Default to company currency
   - **Payment Method**: cash/cheque/etransfer/card/other
   - **Fund/Purpose**: Select a fund
   - **Campaign**: (Optional) Link to campaign
   - **Notes**: Any additional info
4. Click **Save** (state = Draft)
5. Click **Confirm** button
   - Validates required fields
   - Sets state to Confirmed
   - Assigns reference number (e.g., DON-2024-00001)
6. Click **Generate Receipt** button
   - Creates receipt number (e.g., RCP-2024-000001)
   - Sets state to Receipted
   - PDF opens for print/review
7. Click **Print Receipt** to print anytime

## Advanced: Posting to Accounting

For organizations using Odoo Accounting:

1. Open a Receipted donation
2. Select **Journal** (e.g., your bank journal)
3. Click **Post to Accounting** button
   - Creates journal entry
   - Debits bank/cash account
   - Credits donation revenue account
   - Links to donation via move_id
4. Click **View GL Entry** to see accounting entry

## Year-End Reporting

### Generate Donor Year-End Statement

1. Go to **Donations > Reports > Year-End Statements**
2. Select:
   - **Donor**: Choose donor
   - **Tax Year**: Select year (defaults to prior year)
3. View totals:
   - Number of donations
   - Total amount donated
4. Click **Generate PDF Statement**
5. Download comprehensive year-end document
6. Can be sent to donor or used for audit trail

## Testing the Module

### Quick Test Scenario

1. Create a test fund (e.g., "Test Fund")
2. Create a test donor (if not exists)
3. Record a test donation:
   - Amount: 50.00
   - Payment: Cash
   - Fund: Test Fund
4. Confirm donation
5. Generate receipt
6. Print receipt to verify PDF layout
7. (Optional) Post to accounting to test GL

### Expected Behavior

- Donation reference auto-generates (DON-YYYY-#####)
- Receipt number auto-generates when receipt created (RCP-YYYY-######)
- State workflow enforces: Draft → Confirmed → Receipted
- PDF receipt shows all donation details
- GL entry (if posted) shows in Accounting > Journal Entries

## Troubleshooting

### "Donor is required to confirm"
- Ensure donor is selected from dropdown
- Create new contact if donor not in system

### "Donation amount must be greater than zero"
- Enter positive amount
- Check currency conversion if needed

### "Please select a journal to post this donation"
- Go to donation and select Journal field
- Choose your bank/cash journal

### "Fund or journal must be configured with donation account"
- Edit fund and set GL Account
- Or select fund with GL account already assigned

### "No receipted donations found"
- Ensure donations are in Receipted state (not just Confirmed)
- Check date range matches selected year
- Verify donor is selected

### Reports not printing
- Enable JavaScript in browser
- Check browser PDF permissions
- Verify company info filled in (for receipt letterhead)

## Next Steps

- Set up recurring donations (create multiple manually or via workflow)
- Create a backup/schedule of donations
- Train staff on donation entry process
- Configure email notifications for donation confirmations
- Set up permission groups for multi-user access

## Support

For issues or questions:
1. Check README.md for detailed feature documentation
2. Review Odoo logs for error messages
3. Verify all dependencies installed (account, mail)
4. Test with sample data first

---

**Module Ready to Use!**
Start tracking donations and generating tax receipts.
