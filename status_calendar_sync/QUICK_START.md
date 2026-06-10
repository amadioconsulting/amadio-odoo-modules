# Status-to-Calendar Automation – Quick Start (5 minutes)

## Installation (2 minutes)

1. **Copy the module to your Odoo instance**
   ```bash
   cp -r status_calendar_sync /path/to/odoo/addons/
   ```

2. **Update module list**
   - Open Odoo web interface
   - Go to: **Apps** → **Update Apps List**
   - Wait for completion

3. **Install the module**
   - Search for: **"Status-to-Calendar"**
   - Click the result
   - Click **Install**

4. **Verify installation**
   - Go to: **Calendar** → **Configuration** → **Sync Rules**
   - You should see an empty list

## Your First Rule (3 minutes)

Let's create a rule that triggers when a sales order is confirmed:

### Step 1: Open the Rule Creator
- Go to: **Calendar** → **Configuration** → **Sync Rules**
- Click **Create**

### Step 2: Basic Info
- **Rule Name**: `SO Confirm → Follow-up Call`
- **Source Model**: `Sale Order`

### Step 3: Trigger Configuration
- **Trigger Field**: `state` (the field name)
- **Trigger Value**: `sale` (the value that triggers)

### Step 4: Event Configuration
- **Event Name Template**: `Follow-up call for {record_name}`
- **Event Delay (days)**: `3` (create event 3 days after trigger)
- **Event Duration (hours)**: `1`
- **Event Type**: Leave blank (optional)

### Step 5: Assignment
- **Assign To**: `Responsible User`
- **Responsible User Field**: `user_id` (field on Sale Order)

### Step 6: Save
- Click **Save**
- You should see a **Linked Server Action** ID appear in the Advanced tab

## Test It (immediately)

1. **Create a test sales order**
   - Go to: **Sales** → **Orders** → **Create**
   - Fill in basic details (Customer, Product, etc.)
   - Click **Save**

2. **Confirm the order**
   - Click **Confirm Sale**
   - The state changes to "sale"
   - This triggers your rule

3. **Check the calendar**
   - Go to: **Calendar**
   - Look at calendar 3 days from today
   - You should see "Follow-up call for [Order Name]"

## You're Done!

You now have automated calendar events based on status changes. Create more rules for:

- **Projects**: Trigger when task moves to "In Progress"
- **Support**: Trigger when ticket is "Done"
- **Opportunities**: Trigger when stage changes
- **Invoices**: Trigger when status changes to "Posted"

## Common Rules to Set Up

### Rule 2: Project Task Check-in
```
Rule Name: Task Started → Check-in
Model: Project Task
Trigger Field: stage_id
Trigger Value: 4 (adjust to your In Progress stage ID)
Event Name: Check-in: {record_name}
Delay: 0 days
Duration: 0.5 hours
Assign To: Current User
```

### Rule 3: Invoice Verification Reminder
```
Rule Name: Invoice Posted → Verification
Model: Account Invoice
Trigger Field: state
Trigger Value: posted
Event Name: Verify invoice {record_name}
Delay: 7 days
Duration: 0.25 hours
Assign To: Responsible User
Responsible Field: user_id
```

### Rule 4: Opportunity Follow-up
```
Rule Name: Opportunity Moved → Follow-up
Model: CRM Opportunity
Trigger Field: stage_id
Trigger Value: 2 (adjust to your stage)
Event Name: Follow up on {record_name}
Delay: 1 day
Duration: 1 hour
Assign To: Responsible User
Responsible Field: user_id
```

## Troubleshooting

### Events not appearing?
1. Verify rule is **Active** (toggle ON in the tree view)
2. Check you're looking at the right calendar date (event delayed by X days)
3. Make sure you're the assigned user or have calendar access

### Wrong field name?
1. Go to: **Settings** → **Technical** → **Models**
2. Search for your model (e.g., "Sale Order")
3. Open it and find the exact field name in the Fields list
4. Update your rule with the correct field name

### Can't see responsible user?
1. Use dot notation: `user_id`, `customer_id.sales_id`, etc.
2. The final field must link to a user or have a `partner_id`

### Rule created but no server action?
1. Refresh the page
2. Re-open the rule to check Advanced tab
3. If still empty, try Save again

## Advanced Features

### Using Placeholders
```
{record_name}  → Customer name, Order name, etc.
{record_url}   → Direct link to the record in Odoo
```

Example template:
```
Follow-up for {record_name} - Click here: {record_url}
```

### Dot Notation for User Fields
```
user_id              → Direct user field
customer_id.sales_id → Sales rep of the customer
project_id.user_id   → Project manager
```

### Event Descriptions
Add rich context to your calendar events:
```
Call {record_name} customer to confirm delivery.
Record: {record_url}
```

## Next Steps

1. **Create rules for your top 5 business processes**
2. **Train your team on how to view events**
3. **Monitor for the first week and adjust delays as needed**
4. **Consider event types/categories for color coding**

---

**That's it! You're now automating calendar events. Enjoy!**

For full documentation, see:
- `README.md` — Complete user guide
- `INSTALLATION_GUIDE.md` — Detailed setup & troubleshooting
- `TECHNICAL_SPECIFICATION.md` — For developers
