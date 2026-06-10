# Smart Email Template Selector – Installation & Setup Guide

## Module Info
- **Name:** Smart Email Template Selector
- **Module ID:** smart_mail_template
- **Version:** 18.0.1.0.0
- **License:** LGPL-3
- **Author:** AMADIO
- **Website:** https://amadio.io
- **Price:** 59.00 EUR

---

## Installation

### 1. Copy Module to Odoo Addons Directory
```bash
cp -r smart_mail_template /path/to/odoo/addons/
```

### 2. Install via Odoo UI
1. Navigate to **Apps** > **All Modules**
2. Search for "Smart Email Template Selector"
3. Click **Install**

Or via command line:
```bash
odoo --addons-path=/path/to/odoo/addons -d database_name -i smart_mail_template
```

### 3. Verify Installation
- Check **Settings > Technical > Email > Smart Template Rules** menu item appears
- Check **Settings > Technical > Email > Template Usage Analytics** menu item appears

---

## Initial Setup

### Step 1: Create Template Rules
1. Go to **Settings > Technical > Email > Smart Template Rules**
2. Click **Create**
3. Fill in:
   - **Model:** Select the model (e.g., `sale.order`, `crm.lead`)
   - **Email Template:** Choose a template to suggest
   - **Stage Field** (optional): Field name to match (e.g., `state`, `stage_id`)
   - **Stage Value** (optional): Value to match (e.g., `confirmed`, `1`)
   - **Priority:** 0–100 (higher = appears first)
   - **Usage Multiplier:** 0.1–10.0 (weight for frequency scoring)
4. Click **Save**

### Example Rules

**Sales Order – Quote Proposal**
- Model: sale.order
- Template: "Quote Proposal Email"
- Stage Field: state
- Stage Value: draft
- Priority: 90

**Sales Order – Order Confirmation**
- Model: sale.order
- Template: "Order Confirmation Email"
- Stage Field: state
- Stage Value: sale
- Priority: 85

**CRM Lead – Welcome**
- Model: crm.lead
- Template: "Lead Welcome Email"
- Stage Field: (leave blank)
- Priority: 50

---

## How It Works

### Suggested Templates (Smart Suggestions Section)
When composing an email from a sales order, quotation, or any tracked model:
1. The "Smart Suggestions" section appears automatically
2. Templates are sorted by:
   - **Primary:** Priority (0–100, descending)
   - **Secondary:** Your usage frequency (if you've used them before)
3. Shows top 5 most relevant templates
4. Click any suggestion to apply it instantly
5. The click is recorded for future frequency weighting

### Recently Used Templates
Below Smart Suggestions, you'll see your 5 most recently used templates from the past 30 days.
These are personalized per user and help speed up common workflows.

### Usage Tracking
Every time you apply a template (whether suggested or manually selected):
- System records: template used, user, timestamp, count
- Data stored in **smart.mail.template.usage** model
- Viewable in **Settings > Technical > Email > Template Usage Analytics**

---

## Configuration Best Practices

### 1. Organize by Business Process
Create rules grouped by workflow stage, not just template name.

**Example: Quote-to-Invoice Workflow**
```
Sale Draft → "Initial Proposal" (P: 90)
Sale Sent → "Follow-up" (P: 85)
Sale Confirmed → "Order Confirmation" (P: 80)
Invoice Posted → "Invoice Sent" (P: 75)
```

### 2. Use Stage Fields for Precision
Specify stage_field + stage_value to show templates only when they're relevant.
- Reduces clutter
- Improves user experience
- Prevents wrong template application

### 3. Priority Hierarchy
- **90–100:** Must-use, critical path templates
- **70–89:** High-frequency templates for key stages
- **50–69:** Standard, general-purpose templates
- **0–49:** Fallback, rarely-used templates

### 4. Usage Multiplier Fine-Tuning
- **1.0 (default):** Usage frequency has equal weight to priority
- **2.0–3.0:** If templates should "learn" from user behavior
- **0.5:** If templates should stick to static priority regardless of usage

---

## Advanced Configuration

### Viewing Usage Analytics
1. Go to **Settings > Technical > Email > Template Usage Analytics**
2. See which templates your team uses most
3. Filter by user, date range, or template name
4. Group by User or Template to identify patterns

### Testing a Rule
1. Open a **Smart Template Rule** record
2. From a mail composer for that model, you'll see the suggestion
3. Click it to verify it appears and applies correctly

### Disabling a Rule
- Set **Active = False** to disable a rule without deleting it
- Rule won't be suggested, but historical usage is preserved

### Bulk Operations
- Use tree view's checkbox to select multiple rules
- Edit priority or active status in bulk from the form

---

## Troubleshooting

### Smart Suggestions Not Appearing
**Problem:** No "Smart Suggestions" section in mail composer.

**Solutions:**
1. Check module is installed: **Apps > Search "Smart"**
2. Verify rules exist for that model: **Settings > Technical > Email > Smart Template Rules**
3. Check rule is **Active = True**
4. If composing from unsupported model, create a rule for it
5. Restart Odoo server

### Wrong Templates Suggested
**Problem:** Suggestions don't match current record stage.

**Solutions:**
1. Verify rule's **Stage Field** field name matches your model's actual field
2. Verify **Stage Value** exactly matches the current record's field value (case-sensitive)
3. Check **Priority** – lower priority templates may be hidden by higher-priority ones
4. Use **Settings > Email > Template Usage Analytics** to debug which templates have highest scores

### Can't Create a Rule
**Problem:** Model not found or field error.

**Solutions:**
1. Ensure **Model** is selected (not just typed)
2. Verify **Stage Field** is a real field on that model (use Technical inspector)
3. Check constraints: both **Stage Field** and **Stage Value** must be filled, or both blank

### Performance Issues
**Problem:** Suggestions loading slowly.

**Solutions:**
1. Reduce number of rules for that model (archive inactive ones)
2. Prefer specific **Stage Field** filters over generic rules
3. Monitor database query logs – rule matching is SQL-indexed
4. Contact AMADIO support if large-scale optimization needed

---

## Uninstallation

To remove the module:
1. Go to **Apps > Installed Modules**
2. Search for "Smart Email Template Selector"
3. Click menu (...) and **Uninstall**

All tables and menu items are removed. Historical usage data is also deleted.

---

## Support & Documentation

**Author:** AMADIO
**Website:** https://amadio.io
**Module Repository:** [Module build directory]

For issues, feature requests, or customization:
- Contact AMADIO consulting
- Review this guide's troubleshooting section
- Check Odoo logs for detailed error messages

---

## Version History

### 18.0.1.0.0 (Initial Release)
- Smart template suggestions based on model + stage
- Recently used templates per user
- Usage tracking and analytics
- Priority-based scoring with frequency weighting
- Full integration with Odoo 18 mail composer
