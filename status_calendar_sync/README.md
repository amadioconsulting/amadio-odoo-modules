# Status-to-Calendar Automation (P09)

**Production-ready Odoo 18.0 module** for automatic calendar event creation triggered by record status/stage changes.

## Overview

When a record in any Odoo model transitions to a specific status or stage, this module instantly creates a calendar event. Perfect for service businesses that need automated follow-ups and schedule management.

### Example Use Cases

1. **Sales Orders**: When a sale order state becomes "sale" (confirmed), create a "Follow-up call in 3 days" event
2. **Project Tasks**: When a task moves to "In Progress", schedule a "Project check-in" meeting
3. **Support Tickets**: When a ticket is resolved, create a "Customer satisfaction survey" reminder

## Key Features

- **Flexible Trigger**: Monitor any field (status, stage, custom fields) on any model
- **Customizable Events**: Template-based event names and descriptions with placeholders
- **Intelligent Scheduling**: Create events immediately or X days after trigger
- **Smart Assignment**: Assign to current user, responsible user field, or all followers
- **No Coding Required**: Full configuration through UI—no developer intervention needed
- **Server-Side Automation**: Uses base.automation for reliable, model-agnostic triggering
- **Audit Trail**: Full mail.thread integration for transparency

## Installation

1. Copy the `status_calendar_sync` folder to your Odoo `addons` directory
2. Update the module list: Settings → Apps → Update Apps List
3. Search for "Status-to-Calendar Automation" and click Install
4. Go to Calendar → Configuration → Sync Rules to create your first rule

## Creating a Sync Rule

### Step 1: Basic Information
- **Rule Name**: Descriptive name (e.g., "SO Confirm → Follow-up Call")
- **Source Model**: The model to monitor (e.g., Sales Order)
- **Sequence**: Order of evaluation if multiple rules apply

### Step 2: Trigger Configuration
- **Trigger Field**: Field name on the source model (e.g., "state", "stage_id")
- **Trigger Value**: Value to match (e.g., "sale" for state, "3" for stage_id ID)

### Step 3: Event Configuration
- **Event Name Template**: Use `{record_name}` and `{record_url}` placeholders
  - Example: "Follow-up for {record_name}"
- **Event Delay (days)**: Number of days after trigger to schedule event (default: 0 = immediate)
- **Event Duration (hours)**: Calendar event length (default: 1 hour)
- **Event Type/Category**: Optional—for color coding in calendar

### Step 4: Event Description (Optional)
- Template for event description, supports `{record_name}` and `{record_url}` placeholders

### Step 5: Assignment
- **Assign to**: Who should the event appear on?
  - **Current User**: The user who made the change
  - **Responsible User**: A specific field on the source record (e.g., user_id, project_id.user_id)
  - **All Followers**: Everyone following the source record

## Configuration Examples

### Example 1: Sales Order Follow-up Call

| Field | Value |
|-------|-------|
| Rule Name | SO Confirm → Follow-up Call |
| Source Model | Sale Order |
| Trigger Field | state |
| Trigger Value | sale |
| Event Name Template | Follow-up call for {record_name} |
| Event Delay | 3 |
| Event Duration | 1 |
| Assign To | Responsible User |
| Responsible Field | user_id |
| Description | Call customer to confirm satisfaction for {record_name} |

**Result**: When a SO is confirmed, a 1-hour meeting is created 3 days later for the sales rep.

### Example 2: Project Task Check-in

| Field | Value |
|-------|-------|
| Rule Name | Task Started → Project Check-in |
| Source Model | Project Task |
| Trigger Field | stage_id |
| Trigger Value | 4 |
| Event Name Template | Check-in: {record_name} |
| Event Delay | 0 |
| Event Duration | 0.5 |
| Assign To | Current User |
| Description | Review progress on {record_name} |

**Result**: Immediately when a task enters stage 4, a 30-minute check-in is created for whoever moved the task.

### Example 3: Ticket Resolution Notification

| Field | Value |
|-------|-------|
| Rule Name | Ticket Resolved → Follow-up |
| Source Model | Help Desk Ticket |
| Trigger Field | state |
| Trigger Value | done |
| Event Name Template | Ticket {record_name} follow-up |
| Event Delay | 1 |
| Event Duration | 0.25 |
| Assign To | All Followers |
| Description | Check on ticket {record_name} resolution |

**Result**: 1 day after ticket resolution, all team members receive a reminder.

## How It Works (Technical)

1. **Rule Creation**: When you save a calendar sync rule, a `base.automation` server action is automatically created
2. **Field Monitoring**: The server action monitors the configured field on write operations
3. **Trigger Matching**: On each write, the rule checks if the trigger field matches the trigger value
4. **Event Creation**: If matched, a calendar event is created with the specified template and assignment
5. **Logging**: All operations are logged for audit and troubleshooting

### Field Type Support

- **Selection fields**: Trigger value should be the selection key (e.g., "draft", "done")
- **Many2one fields**: Trigger value should be the record ID (e.g., "3" for stage_id.id = 3)
- **Char/Text fields**: Trigger value is matched as string
- **Integer fields**: Trigger value is compared as number

### Placeholder Support

| Placeholder | Content |
|-------------|---------|
| `{record_name}` | Name field of the source record (or ID if no name) |
| `{record_url}` | Odoo menu link to the source record |

## API Reference

### CalendarSyncRule Model

**Fields:**
- `name` (Char, required)
- `active` (Boolean, default=True)
- `model_id` (Many2one to ir.model, required)
- `trigger_field` (Char, required)
- `trigger_value` (Char, required)
- `event_name_template` (Char, required)
- `event_delay_days` (Integer, default=0)
- `event_duration` (Float, default=1.0)
- `event_categ_id` (Many2one to calendar.event.type)
- `assign_to` (Selection: current_user / responsible_user / all_followers)
- `responsible_field` (Char)
- `description_template` (Text)
- `server_action_id` (Many2one to ir.actions.server, readonly)

**Methods:**
- `_create_server_action()`: Generate base.automation server action
- `_trigger_calendar_event_if_matched(record)`: Check trigger and create event
- `_create_calendar_event(source_record)`: Create the calendar event

## Permissions

- **Users**: Can view all sync rules (read-only)
- **System Administrators**: Full CRUD access to sync rules

## Troubleshooting

### Events Not Creating

1. **Check Rule is Active**: In the Sync Rules tree, verify the toggle is ON
2. **Verify Trigger Field**: Ensure the field name exactly matches the model field (e.g., "state", not "status")
3. **Verify Trigger Value**: For many2one fields, use the ID not the name (e.g., "3" for a stage)
4. **Check Server Action**: Open the rule and verify the linked server action exists
5. **Review Logs**: Check Odoo server logs for errors in event creation

### Events Missing Placeholder Content

- **{record_name}**: Ensure the source model has a `name` field
- **{record_url}**: This is automatically populated; no action needed

### Responsible User Field Errors

- Use dot notation for related fields: `project_id.user_id`, `customer_id.sales_id`
- Ensure the final field has a `partner_id` or is a Many2one user field

## Architecture Notes

### Server Action Integration

Each sync rule creates a `base.automation` (ir.actions.server) record that:
- Triggers on every `write()` to the configured model
- Executes Python code that evaluates the rule
- Creates calendar events if conditions match
- Logs all actions for audit trail

### Why Not Webhooks/Signals?

This module uses `base.automation` instead of model signals for:
- **Reliability**: Base automation persists rules to database—survives restarts
- **Scalability**: Centralized automation engine handles all server actions
- **Auditability**: Full integration with Odoo's action logging
- **Flexibility**: Easy enable/disable without code changes

## Version History

- **1.0.0** (March 2026): Initial release for Odoo 18.0

## Support & License

- **Author**: AMADIO
- **Website**: https://amadio.io
- **License**: LGPL-3
- **Price**: €69.00

---

**Built for service businesses. Configured without code. Automated with confidence.**
