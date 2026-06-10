# Smart Email Template Selector – Technical Architecture

## Overview
The Smart Email Template Selector is a lightweight Odoo 18 module that enhances the mail composer with context-aware template suggestions. It uses a rule-based scoring system and per-user usage tracking to surface the most relevant templates.

---

## Data Model

### 1. smart.mail.template.rule
Stores configuration rules for template suggestions.

**Fields:**
- `id` (integer, PK): Record ID
- `model_id` (many2one ir.model): Target model (e.g., sale.order)
- `template_id` (many2one mail.template): Email template to suggest
- `stage_field` (char): Field name to match (e.g., 'state', 'stage_id'). Optional.
- `stage_value` (char): Value to match (e.g., 'confirmed'). Required if stage_field is set.
- `priority` (integer): Sort order. Range: 0–100. Higher = earlier in suggestions.
- `active` (boolean): Enable/disable rule without deleting
- `usage_multiplier` (float): Weight for usage frequency in scoring. Range: 0.1–10.0. Default: 1.0.
- `created_date` (datetime): Record creation timestamp
- `notes` (text): Internal documentation

**Constraints:**
- `priority` must be 0–100
- `usage_multiplier` must be 0.1–10.0
- If `stage_field` is specified, `stage_value` must also be specified (and vice versa)
- Primary key: id
- Unique constraint: None (same model+template+stage can be in multiple rules)

**Indexes:**
- model_id (foreign key)
- template_id (foreign key)
- active (for filtering enabled rules)

**Inheritance:** None
**Access Control:**
- Users: Read-only
- System managers: Full CRUD

---

### 2. smart.mail.template.usage
Tracks per-user, per-template usage statistics.

**Fields:**
- `id` (integer, PK): Record ID
- `template_id` (many2one mail.template): Email template used
- `user_id` (many2one res.users): User who used it
- `use_count` (integer): Total number of times used. Default: 0.
- `last_used` (datetime): Timestamp of most recent use
- `created_date` (datetime): Record creation timestamp

**Constraints:**
- Unique constraint: `(template_id, user_id)` – Each user-template pair appears once
- Primary key: id

**Indexes:**
- (template_id, user_id) – For unique constraint and lookups
- user_id (for "my templates")
- last_used (for sorting by recent)

**Inheritance:** None
**Access Control:**
- Users: Read-only
- System managers: Full CRUD

---

### 3. mail.compose.message (Extended)
Standard Odoo transient model. Smart Mail Template adds computed fields:

**New Fields (computed):**
- `smart_suggested_template_ids` (many2many mail.template): Top 5 templates for current model+stage
- `smart_recently_used_template_ids` (many2many mail.template): User's 5 most recent templates from past 30 days

**New Methods:**
- `_compute_suggested_templates()`: Computes `smart_suggested_template_ids` based on model + stage
- `_compute_recently_used_templates()`: Computes `smart_recently_used_template_ids` from usage table
- `action_apply_suggested_template(template_id)`: Apply template and record usage

---

## Scoring Algorithm

### Suggestion Scoring

When `_compute_suggested_templates()` runs:

1. **Get Model:** Identify ir.model for current model_id (e.g., sale.order)
2. **Load Rules:** Query smart.mail.template.rule where model_id matches and active=True
3. **Filter by Stage:** For each rule, check if:
   - `stage_field` is blank → rule always matches
   - `stage_field` is set → compare target record's field value with `stage_value`
     - Both must match (case-sensitive for char fields)
     - For many2one fields, compare `.name` attribute
4. **Score Matching Rules:** For each rule that passes stage filter:
   ```
   score = (priority * 1000) + (use_count * usage_multiplier)
   ```
   - `priority`: 0–100, primary sort key
   - `use_count`: Frequency from smart.mail.template.usage (0 if no record)
   - `usage_multiplier`: Custom weight (default 1.0)
5. **Rank & Limit:** Sort by score descending, take top 5 unique templates
6. **Return:** List of template IDs ordered by relevance

**Example Calculation:**
```
Rule 1: priority=90, usage_multiplier=1.0, user has 5 uses → score = 90*1000 + 5*1 = 90005
Rule 2: priority=85, usage_multiplier=2.0, user has 3 uses → score = 85*1000 + 3*2 = 85006
Rule 3: priority=70, usage_multiplier=1.0, user has 0 uses → score = 70*1000 + 0*1 = 70000

Rank: Rule 1 (90005) > Rule 2 (85006) > Rule 3 (70000)
```

---

## User Flow

### Composing an Email (Suggested Template Applied)

1. **User opens mail composer** from a record (e.g., sale.order)
   - `mail.compose.message` transient is created
   - `model` field = 'sale.order'
   - `res_id` field = 123 (the order ID)

2. **Form loads** (form view: mail.compose.message)
   - `_compute_suggested_templates()` is triggered
     - Identifies sale.order as model
     - Loads active rules for sale.order
     - Checks current record's stage against rule stage filters
     - Scores and ranks matching rules
     - Returns top 5 template IDs
   - `_compute_recently_used_templates()` is triggered
     - Looks up smart.mail.template.usage for current user
     - Returns 5 most recent from past 30 days

3. **View renders**
   - "Smart Suggestions" section shows top 5 templates as clickable buttons
   - "Recently Used" section shows user's recent templates
   - Standard template selector field remains unchanged

4. **User clicks a suggestion**
   - Calls `action_apply_suggested_template(template_id)`
   - Records usage: smart.mail.template.usage.record_usage()
   - Applies template to compose message: `template_id = template`, then `_onchange_template_id()`
   - User can now edit the email (subject, body, etc.)

5. **User sends email**
   - Standard Odoo mail workflow continues
   - Email is sent, logged on the record

---

## Views & UI

### Smart Mail Template Rule (settings interface)

**Tree View:**
- Columns: model, stage_field, stage_value, template, priority, active
- Default order: priority DESC
- Actions: Create, edit, delete, bulk edit

**Form View:**
- Sections: Rule Configuration, Stage Matching, Notes
- Fields: model_id (required), template_id (required), stage_field, stage_value, priority, usage_multiplier, active, notes, created_date
- Tabs: Main sheet + chatter (for internal notes)

**Search View:**
- Filters: Active, Inactive, High/Medium/Low Priority, With/Without Stage Filter
- Groups: By Model, Template, Priority, Active

**Menu Path:** Settings > Technical > Email > Smart Template Rules

---

### Mail Compose Message (extended form)

**Inherited View:** mail.compose.form

**New Sections (injected before template_id field):**
1. **Smart Suggestions Alert:** Shows if any suggestions exist
2. **Suggested Templates:** Displays top 5 in a read-only many2many tree
3. **Recently Used Alert:** Shows if user has recent templates
4. **Recently Used Templates:** Displays 5 most recent templates

**Behavior:**
- Sections are hidden if no suggestions/recent templates exist (attrs invisible)
- Clicking a suggestion row applies it (via action button or JavaScript)
- Standard template selector field unchanged below suggestions

---

### Smart Mail Template Usage Analytics

**Tree View:**
- Columns: template, user, use_count, last_used
- Default order: last_used DESC
- Actions: View, filter, group

**Search View:**
- Filters: This Week, This Month
- Groups: By User, By Template

**Menu Path:** Settings > Technical > Email > Template Usage Analytics

---

## Installation & Dependencies

**Depends On:**
- `mail` – Odoo's base mail module (provides mail.template, mail.compose.message)

**Python Dependencies:**
- Standard Odoo ORM (models, fields, api decorators)
- datetime module (for usage tracking timestamps)
- logging module (for error handling)

**Database:**
- 2 new tables: smart_mail_template_rule, smart_mail_template_usage
- Foreign key constraints to ir_model, mail_template, res_users
- Created automatically on module install

---

## Security

**Access Control Rules:**
- `smart_mail_template_rule`:
  - base.group_user: Read-only
  - base.group_system: Full CRUD
- `smart_mail_template_usage`:
  - base.group_user: Read-only (analytics)
  - base.group_system: Full CRUD (admin)

**Data Privacy:**
- Usage tracking stores user_id and template_id (no sensitive email content)
- Only system managers can view usage analytics for all users
- Regular users see only suggestions (no usage data exposed in compose view)

---

## Performance Considerations

### Query Optimization
- Rule matching queries are indexed on:
  - model_id (indexed foreign key)
  - active (for quick enabled-rule filtering)
  - template_id (indexed foreign key)
- Usage lookups indexed on (template_id, user_id)

### Caching
- Computed fields are re-calculated on each form load (lightweight operation)
- No persistent cache layer; trades CPU for simplicity and consistency

### Scalability
- Typically fast for < 1000 rules per model
- For larger deployments, consider:
  - Archiving inactive rules
  - Using stage-field filters to narrow rule sets
  - Indexing on priority + model_id for faster sorting

### Database Size
- Minimal growth: ~1 KB per rule, ~0.5 KB per usage record
- Typical small deployment: 100 rules + 10K usage records ≈ 10 MB

---

## Error Handling

### _compute_suggested_templates()
- Catches Exception if model not found, record doesn't exist, or field access fails
- Logs warning with model/record ID
- Returns empty suggested_template_ids (suggestions simply don't appear)
- Compose still works; user sees standard template selector

### record_usage()
- Validates template_id and user_id are not None
- Creates new usage record or updates existing one
- On conflict (unique constraint), update takes precedence

### Stage Field Matching
- Uses hasattr() to safely check if field exists on target record
- Handles both many2one and scalar field types
- Gracefully skips rule if field doesn't exist

---

## Extensibility

### Hooks for Customization
1. **Custom Scoring:** Inherit MailComposeMessage and override `_compute_suggested_templates()`
2. **Additional Rule Fields:** Inherit SmartMailTemplateRule and add fields (e.g., partner_industry_id)
3. **Usage Webhooks:** Inherit SmartMailTemplateUsage and call external APIs in record_usage()
4. **View Customization:** Inherit mail_compose_message_views.xml and modify suggestion rendering

### Future Enhancements (Out of Scope)
- Machine learning ranking based on template success metrics
- Partner-type aware suggestions (e.g., VIP vs. standard partner)
- A/B testing support (track which templates get opened/replied)
- Team-based rule sharing and versioning

---

## Testing Recommendations

### Unit Tests
1. Test rule matching: stage_field / stage_value filtering
2. Test scoring: priority ordering, usage weighting
3. Test usage recording: create and update scenarios
4. Test edge cases: missing fields, null values, invalid data

### Integration Tests
1. Create rules and templates
2. Open mail composer from different models
3. Verify suggestions appear correctly
4. Click suggestions and verify application
5. Verify usage is recorded
6. Check analytics are populated

### Manual Testing
1. Create 3–5 test rules for a common model (e.g., sale.order)
2. Assign different priorities and stage filters
3. Compose emails at different stages (draft, sent, confirmed)
4. Verify suggestions match expected rules
5. Use templates and verify usage tracking
6. Check analytics show correct counts and dates

---

## Maintenance

### Regular Tasks
- **Weekly:** Review template usage analytics for optimization opportunities
- **Monthly:** Archive or delete unused rules
- **Quarterly:** Audit rule priorities and usage multipliers for accuracy

### Common Issues & Fixes
- Suggestions not appearing: Check rule is active, model is correct, stage value matches
- Wrong templates ranked: Verify priority values and usage multiplier weights
- Performance degradation: Archive inactive rules, check database size

### Upgrade Path
- Module version 18.0.1.x.x is stable for Odoo 18
- No breaking changes planned; compatibility maintained with minor updates
