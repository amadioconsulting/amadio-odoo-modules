# SOP Checklist Builder

**Version:** 18.0.1.0.0
**Author:** AMADIO
**Website:** https://amadio.io
**License:** LGPL-3

## Overview

SOP Checklist Builder is a production-grade Odoo 18.0 module that enables organizations to create, manage, and execute Standard Operating Procedure (SOP) templates as reusable checklists. Launch any SOP on any Odoo record (sale order, project, picking, etc.) to create a live checklist instance with real-time completion tracking, critical step enforcement, and complete audit trails.

## Key Features

### Template Management
- Create unlimited reusable SOP templates
- Organize templates by category and code
- Add step-by-step instructions with estimated time
- Mark steps as critical (blocks checklist completion if not done)
- Require evidence attachments for compliance steps
- Optional model filtering (restrict templates to specific Odoo models)
- Duplicate templates for quick variations

### Checklist Execution
- One-click launch of any template on a record
- Template steps automatically copied to a new checklist instance
- Template link remains persistent on the record
- Step-by-step completion tracking
- Real-time progress percentage and step counts
- Visual progress bar in forms

### Step Completion
- Mark steps done individually with a checkbox
- Automatically records user and timestamp
- Optional evidence attachment per step
- Notes field for step-level comments
- Critical step warning banner
- Can reopen or cancel checklists

### Audit & Compliance
- Complete timestamp and user tracking
- Evidence attachment management
- Message thread for process communication
- Workflow blocking on critical steps
- Completion state management (in_progress, completed, cancelled)
- Audit trail of who completed which steps and when

### Integration
- Works with any Odoo model
- Supports custom models and standard models
- Mail module integration for notifications
- Activity tracking with Chatter
- Print-ready checklists

## Module Structure

```
sop_checklist/
├── __init__.py                         # Package initialization
├── __manifest__.py                     # Module metadata
├── README.md                           # This file
├── models/
│   ├── __init__.py                    # Models package initialization
│   ├── sop_template.py                # SOP Template model
│   ├── sop_template_step.py           # SOP Template Step model
│   ├── sop_checklist.py               # SOP Checklist Instance model
│   └── sop_checklist_step.py          # SOP Checklist Step model
├── wizard/
│   ├── __init__.py                    # Wizards package initialization
│   └── launch_checklist_wizard.py     # Launch Checklist Wizard
├── security/
│   └── ir.model.access.csv            # Access control rules
├── views/
│   ├── sop_template_views.xml         # Template list/form/search views
│   └── sop_checklist_views.xml        # Checklist list/form/search views
└── static/
    └── description/
        ├── icon.png                   # Module icon (256x256)
        └── index.html                 # Marketing page
```

## Data Models

### sop.template
Main template model that defines an SOP structure.

**Key Fields:**
- `name` (Char, required) - Template name
- `code` (Char) - Short template code (e.g., "ONBOARD-01")
- `category` (Char) - Category for grouping
- `description` (Text) - Detailed description
- `step_ids` (One2many → sop.template.step) - Template steps
- `step_count` (Integer, computed) - Number of steps
- `critical_step_count` (Integer, computed) - Number of critical steps
- `active` (Boolean, default=True) - Active status
- `applicable_models` (Char) - Comma-separated model names for filtering
- `checklist_count` (Integer, computed) - Number of checklists created from this template

**Key Methods:**
- `action_launch()` - Opens wizard to launch on a record
- `action_duplicate_template()` - Creates a copy with all steps
- `action_view_checklists()` - Shows all checklists from this template
- `get_applicable_models()` - Returns list of applicable models
- `is_applicable_to_model(model_name)` - Checks applicability

### sop.template.step
Individual step within a template.

**Key Fields:**
- `template_id` (Many2one → sop.template, required, cascade) - Parent template
- `sequence` (Integer, default=10) - Display order
- `name` (Char, required) - Step instruction
- `description` (Text) - Detailed how-to notes
- `is_critical` (Boolean, default=False) - Blocks completion if not done
- `requires_evidence` (Boolean, default=False) - Mandate attachment
- `responsible_role` (Char) - Guideline on who does this (e.g., "Manager", "QA Team")
- `estimated_minutes` (Integer) - Time estimate for the step

### sop.checklist
Live checklist instance created from a template.

**Key Fields:**
- `name` (Char) - Auto-generated from template and linked record
- `template_id` (Many2one → sop.template, required) - Source template
- `res_model` (Char, required) - Model name of linked record
- `res_id` (Integer, required) - ID of linked record
- `res_name` (Char) - Display name of linked record
- `state` (Selection) - in_progress / completed / cancelled
- `step_ids` (One2many → sop.checklist.step) - Checklist steps
- `completion_pct` (Float, computed) - Completion percentage
- `steps_done` (Integer, computed) - Number of completed steps
- `steps_total` (Integer, computed) - Total number of steps
- `critical_steps_pending` (Boolean, computed) - Any critical step not done
- `started_by_id` (Many2one → res.users) - User who started
- `date_started` (Datetime) - When checklist was created
- `date_completed` (Datetime) - When marked complete

**Key Methods:**
- `action_complete()` - Mark complete after validating critical steps
- `action_cancel()` - Cancel the checklist
- `action_reopen()` - Reopen a cancelled/completed checklist
- `get_linked_record()` - Get the linked record object
- `action_open_linked_record()` - Action to open linked record

### sop.checklist.step
Individual step in a checklist instance.

**Key Fields:**
- `checklist_id` (Many2one → sop.checklist, required, cascade) - Parent checklist
- `sequence` (Integer) - Display order
- `name` (Char, required) - Step instruction (copied from template)
- `description` (Text) - Detailed notes
- `is_critical` (Boolean) - Copied from template
- `requires_evidence` (Boolean) - Copied from template
- `done` (Boolean, default=False) - Completion status
- `done_by_id` (Many2one → res.users) - User who completed
- `done_date` (Datetime) - When completed
- `evidence_attachment_id` (Many2one → ir.attachment) - Attached file
- `notes` (Text) - Step-level notes

**Key Methods:**
- `@api.onchange('done')` - Auto-sets done_by_id and done_date when marked done

### sop.launch.checklist.wizard
Transient wizard to launch a template on a record.

**Key Fields:**
- `template_id` (Many2one → sop.template, required) - Template to launch
- `res_model` (Char, required) - Model of record
- `res_id` (Integer, required) - ID of record
- `res_name` (Char) - Display name (populated by onchange)
- `notes` (Text) - Optional launch notes

**Key Methods:**
- `action_launch()` - Creates checklist and copies steps

## Usage Examples

### 1. Create an Onboarding SOP Template

1. Go to **SOP Checklist > Templates**
2. Click **Create**
3. Fill in:
   - **Name:** "Employee Onboarding"
   - **Code:** "ONBOARD-01"
   - **Category:** "HR"
4. In the Steps section, add:
   - Step 1: "Collect employee documents" (Critical: Yes, Requires Evidence: Yes)
   - Step 2: "Complete IT setup" (Critical: Yes)
   - Step 3: "Assign office space" (Critical: No)
   - Step 4: "Manager sign-off" (Critical: Yes)
5. Save and go!

### 2. Launch the Checklist on a Contact

1. Open a contact record
2. Use Odoo's "Create" action or context menu to launch the SOP
3. Or go to **SOP Checklist > Templates**, select "Employee Onboarding"
4. Click **Launch on Record**
5. Select the contact and click **Launch Checklist**
6. A new checklist is created and opened in a new form

### 3. Complete the Checklist

1. In the checklist form, for each step:
   - Review the instruction and estimated time
   - If evidence is required, attach a file
   - Check the **Completed** checkbox
   - The system auto-records who did it and when
   - Add notes if needed
2. The progress bar updates in real-time
3. When all critical steps are done, click **Mark Complete**
4. The checklist state changes to "Completed" and date_completed is set

### 4. View Checklist Analytics

- **SOP Checklist > Active Checklists** shows all in-progress checklists
- Filter by state, template, model, or responsible user
- Group by template, model, or state for analytics
- Click any checklist to see step-by-step details

### 5. Duplicate a Template

1. Open a template
2. Click **Duplicate**
3. A copy is created with all steps
4. Edit the copy as needed for variations

## Access Control

The module includes predefined access rules:

- **User** - Can read templates, create/edit/read checklists and steps (cannot delete)
- **Manager** (System) - Full create/read/write/delete access to all models

Additional user groups can be created for role-based access:
- Template Creators - Create and manage templates
- Checklist Executors - Launch and complete checklists
- Audit Managers - View-only access to completed checklists

## Installation

1. Copy the `sop_checklist` directory to your Odoo `addons_path`
2. Update your module list: **Settings > Apps > Update Apps List**
3. Search for "SOP Checklist Builder" and click **Install**
4. The module is now active and ready to use

## Dependencies

- **Odoo 18.0**
- **Python 3.10+**
- **PostgreSQL 13+**
- **mail** module (for Chatter integration)
- **base** module (standard)

## Configuration

### Optional: Restrict Templates to Models

In a template's **Applicable Models** field, enter comma-separated model names to restrict launches to those models only:

```
sale.order, project.project, purchase.order
```

Leave empty to allow launching on any model.

### Optional: Custom Roles

Create new user groups and assign them to control template creation, checklist launching, or completion permissions:

1. Go to **Settings > Manage Users > Groups**
2. Create a new group (e.g., "SOP Template Creators")
3. In the group, assign users and set model access rules
4. In each template/checklist record, use the access controls to restrict visibility

## API Reference

### Launch a Checklist Programmatically

```python
# From another module or custom code
template = self.env['sop.template'].search([('code', '=', 'ONBOARD-01')], limit=1)
checklist = self.env['sop.checklist'].create({
    'template_id': template.id,
    'res_model': 'res.partner',
    'res_id': 5,
    'res_name': 'Acme Corp',
})

# Copy template steps
for step in template.step_ids:
    self.env['sop.checklist.step'].create({
        'checklist_id': checklist.id,
        'sequence': step.sequence,
        'name': step.name,
        'description': step.description,
        'is_critical': step.is_critical,
        'requires_evidence': step.requires_evidence,
    })

# Mark step complete
checklist.step_ids[0].write({
    'done': True,
    'done_by_id': self.env.user.id,
    'done_date': fields.Datetime.now(),
})

# Complete checklist
if not checklist.critical_steps_pending:
    checklist.action_complete()
```

### Query Checklists

```python
# Get all in-progress checklists for a sale order
checklists = self.env['sop.checklist'].search([
    ('state', '=', 'in_progress'),
    ('res_model', '=', 'sale.order'),
    ('res_id', '=', 123),
])

# Get completion percentage
print(f"Completion: {checklist.completion_pct}%")

# Check if critical steps are pending
if checklist.critical_steps_pending:
    print("Workflow is blocked - complete critical steps first")

# Get audit trail
for step in checklist.step_ids:
    print(f"{step.name}: Done by {step.done_by_id.name} at {step.done_date}")
```

## Troubleshooting

### Checklist Won't Mark Complete

**Issue:** "Cannot complete checklist. X critical step(s) still pending"

**Solution:** Review the checklist form. Look for the red warning banner listing critical steps. Mark each critical step as done by checking its checkbox.

### Template Not Showing in Launch

**Issue:** Template doesn't appear when launching a checklist

**Solution:** Check the template's **Applicable Models** field. If it has a value, ensure your record's model is in the comma-separated list.

### Evidence Attachment Not Required

**Issue:** Step shows "Requires Evidence" but allows completion without attachment

**Solution:** The module does not enforce evidence attachment at save time—it's a UI guideline. Implement custom validation in your workflow if needed.

### Timestamp Showing Wrong User

**Issue:** Completed step shows wrong "Completed By" user

**Solution:** The system records the current user when the step is marked done. Ensure you're logged in as the correct user when completing steps.

## Performance Notes

- Templates with 100+ steps work fine but may slow down UI rendering
- For large deployments, consider archiving old checklists annually
- Checklist queries are indexed on template_id and state for fast filtering
- Message thread/Chatter may grow large—consider periodic cleanup of old threads

## Customization & Extensions

The module is built with standard Odoo patterns and can be extended:

1. **Add custom fields** to sop.template or sop.checklist
2. **Create custom computed fields** (e.g., SLA tracking, assigned user per step)
3. **Add validation** via `@api.constrains`
4. **Create reports** using qweb (print checklist with custom formatting)
5. **Integrate with workflows** by overriding `action_complete()`
6. **Extend the wizard** to add pre-launch validation

## Security & Privacy

- All checklist data is stored in the Odoo database with standard security
- Access is controlled via group-based access rules
- Evidence attachments follow Odoo's attachment security model
- Audit trail is immutable (no step deletion, only state changes)
- Message thread provides non-repudiation for critical steps

## Support & Maintenance

For issues, enhancements, or questions:
- Visit **https://amadio.io**
- Report bugs via the Odoo Apps community channels
- Request features via AMADIO consulting engagement

---

**SOP Checklist Builder** - Making every process consistent, auditable, and done right every time.
