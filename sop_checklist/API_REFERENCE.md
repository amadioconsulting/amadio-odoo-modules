# SOP Checklist Builder - Technical API Reference

## Models Overview

### sop.template

The SOP template is the reusable blueprint for checklists. It defines steps, criticality, and model applicability.

#### Model Name
```
sop.template
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | Char | Yes | Template name |
| code | Char | No | Short code (e.g., "ONBOARD-01") |
| category | Char | No | Category for grouping |
| description | Text | No | Detailed description |
| sequence | Integer | No | Display order (default=10) |
| step_ids | One2many | No | Related template steps |
| step_count | Integer | Computed | Number of steps |
| critical_step_count | Integer | Computed | Number of critical steps |
| active | Boolean | No | Active status (default=True) |
| applicable_models | Char | No | Comma-separated model names for filtering |
| checklist_count | Integer | Computed | Number of checklists created from this template |

#### Inheritance
- `mail.thread` - Message threading and activity tracking
- `mail.activity.mixin` - Activity management

#### Methods

##### action_launch()
Opens the launch wizard to create a checklist on a record.

```python
template.action_launch()
```

**Returns:** Dictionary with window action for launching

**Example:**
```python
template = self.env['sop.template'].browse(5)
action = template.action_launch()
# Opens launch wizard for this template
```

---

##### action_duplicate_template()
Creates a copy of this template with all its steps.

```python
template.action_duplicate_template()
```

**Returns:** Dictionary with window action showing the new template

**Example:**
```python
template = self.env['sop.template'].browse(5)
action = template.action_duplicate_template()
# New template created with name "Original Name (Copy)"
```

---

##### action_view_checklists()
Shows all checklists created from this template.

```python
template.action_view_checklists()
```

**Returns:** Dictionary with window action filtered to this template's checklists

**Example:**
```python
template = self.env['sop.template'].browse(5)
action = template.action_view_checklists()
# Opens checklist list filtered by this template
```

---

##### get_applicable_models()
Returns list of model names this template can be launched on.

```python
models = template.get_applicable_models()
```

**Returns:** List of strings, or None if applicable to all models

**Example:**
```python
template = self.env['sop.template'].browse(5)
applicable = template.get_applicable_models()
# Returns ['sale.order', 'project.project'] or None
```

---

##### is_applicable_to_model(model_name)
Checks if this template can be launched on the given model.

```python
is_applicable = template.is_applicable_to_model('sale.order')
```

**Args:**
- `model_name` (str) - Odoo model name

**Returns:** Boolean

**Example:**
```python
template = self.env['sop.template'].browse(5)
if template.is_applicable_to_model('sale.order'):
    # Can launch on sale orders
    pass
```

---

### sop.template.step

Individual step within a template. Steps define the checklist structure.

#### Model Name
```
sop.template.step
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | Many2one (sop.template) | Yes | Parent template (cascade delete) |
| sequence | Integer | No | Display order (default=10) |
| name | Char | Yes | Step instruction |
| description | Text | No | Detailed how-to notes |
| is_critical | Boolean | No | Blocks checklist completion if unchecked (default=False) |
| requires_evidence | Boolean | No | Mandate attachment to complete (default=False) |
| responsible_role | Char | No | Guideline on who should do this (e.g., "Manager") |
| estimated_minutes | Integer | No | Time estimate for the step |

#### SQL Constraints
- `sequence >= 0` - Sequence must be non-negative
- `estimated_minutes >= 0` - Time estimate must be non-negative

#### Special Behavior
When `template_id` changes via onchange, sequence is auto-set to the next available (max_sequence + 10).

---

### sop.checklist

A live checklist instance created from a template. Each checklist is linked to a specific record and tracks completion.

#### Model Name
```
sop.checklist
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | Char | Yes | Auto-generated from template and record |
| template_id | Many2one (sop.template) | Yes | Source template |
| res_model | Char | Yes | Odoo model name of linked record |
| res_id | Integer | Yes | ID of linked record |
| res_name | Char | No | Display name of linked record (stored snapshot) |
| state | Selection | No | in_progress / completed / cancelled (default=in_progress) |
| step_ids | One2many (sop.checklist.step) | No | Checklist steps |
| completion_pct | Float | Computed | Percentage of steps done (0-100) |
| steps_done | Integer | Computed | Number of completed steps |
| steps_total | Integer | Computed | Total number of steps |
| critical_steps_pending | Boolean | Computed | True if any critical step is not done |
| started_by_id | Many2one (res.users) | No | User who created checklist (default=current user) |
| date_started | Datetime | No | When checklist was created (default=now) |
| date_completed | Datetime | No | When marked complete |

#### Inheritance
- `mail.thread` - Message threading and activity tracking
- `mail.activity.mixin` - Activity management

#### SQL Constraints
- `res_id > 0` - Record ID must be positive
- `completion_pct >= 0 AND completion_pct <= 100` - Percentage must be 0-100

#### Computed Fields

##### completion_pct
```python
completion_pct = (steps_done / steps_total) * 100 if steps_total > 0 else 0
```

Stored for performance. Updated whenever step_ids change.

##### steps_done
Count of `step_ids` where `done = True`. Stored, indexed.

##### steps_total
Count of total `step_ids`. Stored, indexed.

##### critical_steps_pending
True if `step_ids.filtered(lambda s: s.is_critical and not s.done)` is non-empty. Stored, indexed.

#### Methods

##### action_complete()
Mark checklist as completed. Validates all critical steps are done first.

```python
checklist.action_complete()
```

**Raises:**
- `UserError` if already completed
- `UserError` if critical steps are pending

**Side Effects:**
- Sets `state = 'completed'`
- Sets `date_completed = now()`
- Posts message to thread: "Checklist completed by [user]"

**Example:**
```python
checklist = self.env['sop.checklist'].browse(5)
try:
    checklist.action_complete()
except UserError as e:
    print(f"Cannot complete: {e}")
```

---

##### action_cancel()
Cancel the checklist without completing.

```python
checklist.action_cancel()
```

**Raises:**
- `UserError` if already cancelled

**Side Effects:**
- Sets `state = 'cancelled'`
- Posts message to thread: "Checklist cancelled by [user]"

**Example:**
```python
checklist = self.env['sop.checklist'].browse(5)
checklist.action_cancel()
```

---

##### action_reopen()
Reopen a cancelled or completed checklist.

```python
checklist.action_reopen()
```

**Side Effects:**
- Sets `state = 'in_progress'`
- Clears `date_completed`
- Posts message to thread: "Checklist reopened by [user]"

**Example:**
```python
checklist = self.env['sop.checklist'].browse(5)
checklist.action_reopen()
```

---

##### get_linked_record()
Get the linked record object (if it still exists).

```python
record = checklist.get_linked_record()
```

**Returns:**
- Record object if exists, or None

**Example:**
```python
checklist = self.env['sop.checklist'].browse(5)
sale_order = checklist.get_linked_record()
if sale_order:
    print(f"Checklist is for: {sale_order.name}")
```

---

##### action_open_linked_record()
Odoo action to open the linked record in a form.

```python
action = checklist.action_open_linked_record()
```

**Returns:** Window action dictionary

**Raises:** `UserError` if linked record no longer exists

**Example:**
```python
checklist = self.env['sop.checklist'].browse(5)
return checklist.action_open_linked_record()
# Opens the linked sale order or other model
```

---

### sop.checklist.step

Individual step in a checklist instance. Steps track completion status and evidence.

#### Model Name
```
sop.checklist.step
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| checklist_id | Many2one (sop.checklist) | Yes | Parent checklist (cascade delete) |
| sequence | Integer | No | Display order |
| name | Char | Yes | Step instruction (copied from template) |
| description | Text | No | Detailed notes (copied from template) |
| is_critical | Boolean | No | Copied from template (default=False) |
| requires_evidence | Boolean | No | Copied from template (default=False) |
| done | Boolean | No | Completion status (default=False) |
| done_by_id | Many2one (res.users) | No | User who completed |
| done_date | Datetime | No | When completed |
| evidence_attachment_id | Many2one (ir.attachment) | No | Attached file (proof of completion) |
| notes | Text | No | Step-level notes and comments |

#### Special Behavior

When `done` changes via onchange:
- If set to True:
  - `done_by_id` → current user (if not already set)
  - `done_date` → now (if not already set)
- If set to False:
  - `done_by_id` → clear
  - `done_date` → clear
  - `evidence_attachment_id` → clear

All changes to `done` are tracked (mail.thread).

#### Example

```python
# Mark step complete
step = self.env['sop.checklist.step'].browse(5)
step.write({'done': True})
# Automatically sets:
# - done_by_id = current user
# - done_date = now

# Add evidence later
step.evidence_attachment_id = attachment.id

# Unmark step
step.write({'done': False})
# Automatically clears:
# - done_by_id
# - done_date
# - evidence_attachment_id
```

---

### sop.launch.checklist.wizard

Transient wizard to launch a template on a record. Not persistent—discarded after use.

#### Model Name
```
sop.launch.checklist.wizard
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | Many2one (sop.template) | Yes | Template to launch |
| res_model | Char | Yes | Model name of target record |
| res_id | Integer | Yes | ID of target record |
| res_name | Char | No | Display name (populated by onchange) |
| notes | Text | No | Optional launch notes |

#### Methods

##### action_launch()
Create a checklist and copy template steps. Transient model—clears after creation.

```python
wizard.action_launch()
```

**Returns:** Window action to open the newly created checklist

**Raises:**
- `UserError` if template is not applicable to the model
- `UserError` if record doesn't exist

**Side Effects:**
- Creates new `sop.checklist` record
- Creates `sop.checklist.step` records by copying from template
- Posts message to checklist: "SOP launched with notes: [notes]"

**Example:**
```python
wizard = self.env['sop.launch.checklist.wizard'].create({
    'template_id': 5,
    'res_model': 'sale.order',
    'res_id': 10,
    'notes': 'Launching for important client',
})
action = wizard.action_launch()
# Creates checklist and opens it
```

---

## Common Queries

### Get all active templates
```python
templates = self.env['sop.template'].search([('active', '=', True)])
```

### Get in-progress checklists for a sale order
```python
checklists = self.env['sop.checklist'].search([
    ('state', '=', 'in_progress'),
    ('res_model', '=', 'sale.order'),
    ('res_id', '=', order_id),
])
```

### Get pending critical steps
```python
pending_steps = checklist.step_ids.filtered(
    lambda s: s.is_critical and not s.done
)
```

### Get completed checklists by user
```python
completed = self.env['sop.checklist'].search([
    ('state', '=', 'completed'),
    ('started_by_id', '=', user_id),
])
```

### Get checklists by completion percentage
```python
# Find checklists that are 50-75% complete
partial = self.env['sop.checklist'].search([
    ('completion_pct', '>=', 50),
    ('completion_pct', '<=', 75),
])
```

### Get most used templates
```python
templates = self.env['sop.template'].search([])
templates = sorted(templates, key=lambda t: t.checklist_count, reverse=True)
```

### Get templates with critical steps
```python
critical = self.env['sop.template'].search([
    ('critical_step_count', '>', 0)
])
```

---

## Custom Code Examples

### Programmatically Create and Launch a Checklist

```python
from odoo import models, fields

class SaleOrderExtension(models.Model):
    _inherit = 'sale.order'

    def auto_launch_fulfillment_sop(self):
        """Auto-launch fulfillment SOP when order is confirmed."""
        template = self.env['sop.template'].search(
            [('code', '=', 'FULFILLMENT-01')], limit=1
        )
        if not template:
            return

        # Create checklist
        checklist = self.env['sop.checklist'].create({
            'template_id': template.id,
            'res_model': 'sale.order',
            'res_id': self.id,
            'res_name': self.name,
        })

        # Copy steps
        for step in template.step_ids:
            self.env['sop.checklist.step'].create({
                'checklist_id': checklist.id,
                'sequence': step.sequence,
                'name': step.name,
                'description': step.description,
                'is_critical': step.is_critical,
                'requires_evidence': step.requires_evidence,
            })

        # Post message
        self.message_post(
            body=f"Fulfillment SOP checklist created: {checklist.name}",
            message_type='notification',
        )
```

### Check Completion Before Workflow Action

```python
def action_delivery_ready(self):
    """Only allow delivery if SOP checklist is complete."""
    # Find associated checklist
    checklist = self.env['sop.checklist'].search([
        ('res_model', '=', 'sale.order'),
        ('res_id', '=', self.id),
        ('state', '=', 'in_progress'),
    ], limit=1)

    if checklist:
        raise UserError(
            f"Cannot proceed to delivery. "
            f"Checklist '{checklist.name}' is still in progress. "
            f"Completion: {checklist.completion_pct}%"
        )

    # Proceed with delivery
    self.write({'state': 'shipping'})
```

### Get Checklist Progress Report

```python
def get_checklist_report(self):
    """Generate report of all checklists."""
    checklists = self.env['sop.checklist'].search([])

    report = []
    for checklist in checklists:
        pending_steps = checklist.step_ids.filtered(lambda s: not s.done)
        pending_critical = checklist.step_ids.filtered(
            lambda s: s.is_critical and not s.done
        )

        report.append({
            'name': checklist.name,
            'template': checklist.template_id.name,
            'record': f"{checklist.res_model}({checklist.res_id})",
            'completion': f"{checklist.completion_pct}%",
            'pending_total': len(pending_steps),
            'pending_critical': len(pending_critical),
            'state': checklist.state,
            'started_by': checklist.started_by_id.name,
            'started_at': checklist.date_started,
        })

    return report
```

### Evidence Validation

```python
def validate_evidence_attachments(self):
    """Ensure all evidence-required steps have attachments."""
    issues = []

    for step in self.step_ids:
        if step.requires_evidence and not step.evidence_attachment_id:
            issues.append(f"{step.name} - Missing evidence")

    if issues:
        raise UserError(
            "Cannot complete checklist. Missing evidence:\n" +
            "\n".join(f"• {issue}" for issue in issues)
        )
```

---

## Security & Access Control

The module includes predefined access rules in `security/ir.model.access.csv`:

- **User Group** - Read templates, read/write checklists and steps (no delete)
- **System/Manager** - Full CRUD access to all models

To create custom access rules:

```python
# In a separate module or custom security file
[(
    'id', 'name', 'model_id:id', 'group_id:id',
    'perm_read', 'perm_write', 'perm_create', 'perm_unlink'
),
 (
    'access_sop_viewer', 'SOP Viewer',
    'model_sop_checklist', 'my_custom_group',
    '1', '0', '0', '0'  # Read-only
),
]
```

---

## Signals & Hooks

The module uses standard Odoo hooks for extensibility:

### `@api.model_create_multi`
Overridden on `sop.checklist.create()` to auto-generate the name.

### `@api.depends()`
Used on computed fields:
- `step_count`, `critical_step_count` on template
- `steps_done`, `steps_total`, `completion_pct`, `critical_steps_pending` on checklist

### `@api.onchange('done')`
On checklist step to auto-set `done_by_id` and `done_date`.

### `@api.onchange('template_id')`
On template step to auto-set next sequence.

### message_post()
Called in `action_complete()`, `action_cancel()`, `action_reopen()` for audit trail.

---

## Testing

Example test case:

```python
from odoo.tests import TransactionCase

class TestSOPChecklist(TransactionCase):
    def setUp(self):
        super().setUp()
        self.template = self.env['sop.template'].create({
            'name': 'Test SOP',
            'code': 'TEST-01',
        })

    def test_create_checklist(self):
        """Test creating a checklist from a template."""
        checklist = self.env['sop.checklist'].create({
            'template_id': self.template.id,
            'res_model': 'sale.order',
            'res_id': 1,
        })
        self.assertEqual(checklist.state, 'in_progress')
        self.assertEqual(checklist.completion_pct, 0.0)

    def test_complete_step(self):
        """Test marking a step complete."""
        step = self.env['sop.checklist.step'].create({
            'checklist_id': checklist.id,
            'name': 'Test Step',
        })
        step.done = True
        self.assertTrue(step.done)
        self.assertEqual(step.done_by_id, self.env.user)
        self.assertIsNotNone(step.done_date)

    def test_critical_blocking(self):
        """Test critical steps block completion."""
        step = self.env['sop.checklist.step'].create({
            'checklist_id': checklist.id,
            'name': 'Critical Step',
            'is_critical': True,
        })
        with self.assertRaises(UserError):
            checklist.action_complete()

        step.done = True
        # Should not raise now
        checklist.action_complete()
        self.assertEqual(checklist.state, 'completed')
```

---

## Performance Optimization Tips

1. **Bulk Create Steps:**
   ```python
   steps_vals = [
       {'checklist_id': cid, 'name': 'Step 1', ...},
       {'checklist_id': cid, 'name': 'Step 2', ...},
   ]
   self.env['sop.checklist.step'].create(steps_vals)
   ```

2. **Use Search Filters:**
   ```python
   # Bad: Load all checklists
   all_checklists = self.env['sop.checklist'].search([])
   in_progress = [c for c in all_checklists if c.state == 'in_progress']

   # Good: Filter at database level
   in_progress = self.env['sop.checklist'].search([
       ('state', '=', 'in_progress')
   ])
   ```

3. **Archive Old Checklists:**
   ```python
   # Mark completed checklists from 2 years ago as archived
   from datetime import datetime, timedelta
   old_date = datetime.now() - timedelta(days=365*2)
   old = self.env['sop.checklist'].search([
       ('state', '=', 'completed'),
       ('date_completed', '<', old_date),
   ])
   # Don't delete—archive or export for compliance
   ```

---

## Version History

- **18.0.1.0.0** (Initial Release)
  - Complete SOP template and checklist system
  - Step-by-step completion tracking
  - Critical step enforcement
  - Evidence attachment support
  - Audit trail with timestamps and users
  - Works with any Odoo model
  - Production-ready for Odoo 18.0

---

End of API Reference
