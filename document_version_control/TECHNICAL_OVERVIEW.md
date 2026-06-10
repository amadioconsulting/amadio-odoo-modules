# Document Version Control - Technical Overview

## Architecture

### Model Hierarchy

```
document.version (models.Model)
├── Tracks versioned document attachments
├── Supports state machine: draft → active/superseded/rejected
└── Integrates with mail.thread for chatter

document.version.mixin (models.AbstractModel)
├── Provides document_version_ids One2many
├── Provides document_version_count computed field
└── Helper actions for opening version management

document.version.upload.wizard (models.TransientModel)
├── File upload interface
├── Automatic version creation
└── Optional approval workflow
```

## Key Design Decisions

### 1. State Machine Design
- **draft**: Initial state, awaiting approval if required
- **active**: Currently live version
- **superseded**: Replaced by newer version (never deleted)
- **rejected**: Approval denied

Automatic superseding of previous active versions on approval ensures only one "active" version exists per document name per record.

### 2. Mixin Pattern
The `document.version.mixin` abstract model allows adding versioning to ANY model with minimal code:

```python
class MyModel(models.Model):
    _inherit = ['my.model', 'document.version.mixin']
    # That's it!
```

Computed fields calculate versions on-the-fly using res_model/res_id matching, avoiding complexity.

### 3. No Deletions, Only Archiving
Versions are marked as "superseded" or "rejected", never physically deleted. This ensures:
- Complete audit trail
- Regulatory compliance
- Historical reference availability
- No accidental data loss

### 4. Approval Workflow
Optional but powerful:
- Check "Approval Required" during upload
- Version starts in Draft
- Authorized users approve/reject
- On approval: state→active, previous active→superseded
- Tracked in chatter for full transparency

### 5. File Handling
Uses Odoo's standard `ir.attachment` model:
- Leverage Odoo's file storage system (local/S3/etc.)
- Integrate seamlessly with Documents module
- Support any file type without restriction
- Automatic file size tracking

## Database Schema

### document_version Table
```sql
- id (Integer) PK
- name (Char) - Document title
- version_number (Char) - Version identifier
- res_model (Char) - Related model
- res_id (Integer) - Related record ID
- attachment_id (Many2one ir.attachment) - File reference
- file_name (Char) - Computed from attachment
- file_size (Integer) - Computed from attachment
- state (Selection) - Current state
- approval_required (Boolean) - Approval needed
- author_id (Many2one res.users) - Uploader
- approved_by_id (Many2one res.users) - Approver
- date (Datetime) - Upload timestamp
- notes (Text) - Change notes
- previous_version_id (Many2one) - Link to prior version
- message_ids (One2many mail.message) - Chatter
- message_follower_ids (Many2many) - Followers
- create_date, create_uid, write_date, write_uid (Standard)
```

## Inheritance & Extension Points

### Extending document.version

```python
# Add custom fields/logic
class DocumentVersion(models.Model):
    _inherit = 'document.version'
    
    custom_field = fields.Char()
    
    def action_approve(self):
        super().action_approve()
        # Custom approval logic
        self.env['audit.log'].create({
            'action': 'approve_version',
            'document_id': self.id,
        })
```

### Adding to Custom Models

```python
# Option 1: Mixin inheritance
class Contract(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'document.version.mixin']

# Option 2: Manual One2many
class CustomModel(models.Model):
    _name = 'custom.model'
    
    document_versions = fields.One2many(
        'document.version',
        compute='_compute_document_versions'
    )
```

## Security & Access Control

### User Permissions
- **Standard Users**: Read/Write/Create document versions, no delete
- **System/Admin Users**: Full CRUD permissions
- Granular control via `ir.model.access` records

### Record Access
- Document versions follow parent record's access rules
- Users accessing a record can see its versions
- No additional role-based restrictions

## Performance Considerations

### Optimization Points
1. **Computed Fields**: `file_name`, `file_size`, `version_label` are stored to avoid repeated computation
2. **One2many Calculation**: `document_version_ids` computed on-demand using domain search
3. **Indexing**: res_model + res_id combination indexed for fast lookups
4. **Attachment Reuse**: Leverages existing ir.attachment index structure

### Scalability
- Efficient for up to 1000s of versions per record
- Pagination in list views for large version histories
- No recursive queries or expensive joins

## Integration Points

### Chatter (mail.thread)
- All versions logged as mail.message records
- Approval/rejection actions trigger notifications
- Team followers automatically notified of version changes
- Full discussion thread on each version

### Attachments (ir.attachment)
- Document versions store file in standard ir.attachment
- Can be integrated with Documents module
- Compatible with cloud storage backends

### Workflow Automation
- State changes can trigger document.workflow actions
- Approval events can be used for automation rules
- Version uploads can auto-assign tasks

## API Reference

### Create a Version Programmatically

```python
# Create attachment
attachment = self.env['ir.attachment'].create({
    'name': 'contract.pdf',
    'datas': base64_file_content,
    'res_model': 'sale.order',
    'res_id': 123,
})

# Create version
version = self.env['document.version'].create({
    'name': 'Service Agreement',
    'version_number': '1.0',
    'res_model': 'sale.order',
    'res_id': 123,
    'attachment_id': attachment.id,
    'notes': 'Initial version',
    'approval_required': True,
})
```

### Get Versions for a Record

```python
versions = self.env['document.version'].search([
    ('res_model', '=', 'sale.order'),
    ('res_id', '=', 123),
    ('state', '=', 'active'),
])
```

### Approve a Version

```python
version.action_approve()
# Automatically supersedes previous active versions with same name
```

## XML View Structure

### Form View Sections
1. **Header**: State bar + Action buttons (Approve, Reject, Supersede)
2. **Button Box**: Link to all versions for this record
3. **Title**: Document name with version number
4. **Metadata**: Version number, author, date, file info
5. **Approval Info**: Approval required flag, approver tracking
6. **Notes**: Change description
7. **Chatter**: Message thread and followers

### List View Columns
- Document name
- Version number
- Author
- Upload date
- Current state (badge with colors)
- File name

## Testing Checklist

- [ ] Upload document without version number
- [ ] Upload with version number
- [ ] Create version requiring approval (stays draft)
- [ ] Approve draft version (becomes active, previous superseded)
- [ ] Reject draft version
- [ ] Manually supersede active version
- [ ] Verify chatter messages created
- [ ] Test on custom model using mixin
- [ ] Verify file download from attachment
- [ ] Test bulk actions on versions
- [ ] Verify security permissions enforced

## Future Enhancement Ideas

1. **Bulk Upload**: Upload multiple versions at once
2. **Comparison View**: Side-by-side diff of versions
3. **Template Versions**: Reusable document templates with versions
4. **Version Locking**: Prevent modification of versions
5. **Advanced Workflows**: Multi-stage approval chains
6. **Version Tags**: Label versions with custom tags/categories
7. **Expiration**: Auto-supersede versions after period
8. **Notifications**: Custom notification rules per model

---

**Module Version**: 18.0.1.0
**License**: LGPL-3.0
**Author**: AMADIO
