# Document Version Control

A production-quality Odoo 18.0 module that adds versioned document attachment management to any Odoo record.

## Features

- **Versioned Documents**: Attach documents with version numbers and track all revisions
- **Complete History**: View full version history on any record; nothing is deleted, only archived
- **Approval Workflow**: Optional approval required before a version goes live
- **Any Model Support**: Inherit the `document.version.mixin` to add versioning to any model
- **File Type Agnostic**: Upload any file format (PDF, Word, Excel, images, etc.)
- **Chatter Integration**: All versions logged in Odoo's Chatter for team visibility
- **Audit Trail**: Full tracking of who uploaded, approved, and when

## Installation

1. Copy the `document_version_control` folder to your Odoo addons directory
2. Update the module list in Odoo
3. Install the module

## Usage

### Adding Document Versioning to a Model

```python
from odoo import models

class Contract(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'document.version.mixin']

    # Your model fields here...
```

### In Views

Add the smart button template to your form view:

```xml
<sheet>
    <div class="oe_button_box" name="button_box">
        <button name="action_open_document_versions" type="object"
                class="oe_stat_button" icon="fa-file">
            <field name="document_version_count" widget="statinfo" string="Versions"/>
        </button>
    </div>
    <!-- Rest of your form -->
</sheet>
```

Or use the template directly:

```xml
<t t-call="document_version_control.document_version_button_box"/>
```

### Uploading Documents

Users can upload new versions through:

1. **Upload Wizard**: Click the "Versions" smart button, then use the upload wizard
2. **Inline Upload**: Direct file selection in the version management view

### Approval Workflow

1. Upload document with "Approval Required" checked
2. Version starts in **Draft** state
3. Authorized users review and click **Approve**
4. Version becomes **Active**, previous active versions become **Superseded**
5. Or click **Reject** if the version doesn't meet requirements

## Models

### document.version

Core model for managing document versions.

**Fields:**
- `name` (Char) - Document title
- `version_number` (Char) - Version identifier (e.g., "1.0", "Rev-A")
- `res_model` (Char) - Related model name
- `res_id` (Integer) - Related record ID
- `attachment_id` (Many2one ir.attachment) - The actual file
- `state` (Selection) - draft, active, superseded, rejected
- `approval_required` (Boolean) - Requires approval before active
- `author_id` (Many2one res.users) - Who uploaded it
- `approved_by_id` (Many2one res.users) - Who approved it
- `date` (Datetime) - Upload date
- `notes` (Text) - Change notes
- `previous_version_id` (Many2one) - Link to prior version

**Methods:**
- `action_approve()` - Approve and set active (supersedes previous)
- `action_reject()` - Reject the version
- `action_supersede()` - Manually mark as superseded

### document.version.mixin

Abstract model to add versioning to any model.

**Fields:**
- `document_version_ids` (One2many) - All versions for this record
- `document_version_count` (Integer) - Count of versions

**Methods:**
- `action_open_document_versions()` - Open versions window action
- `action_open_upload_wizard()` - Open upload wizard

### document.version.upload.wizard

Transient model for the file upload wizard.

**Fields:**
- `name` (Char) - Document title
- `version_number` (Char) - Version identifier
- `attachment` (Binary) - File data
- `attachment_filename` (Char) - Filename
- `notes` (Text) - Change notes
- `approval_required` (Boolean) - Require approval

**Methods:**
- `action_upload()` - Create attachment and version

## Security

Access control is managed through:
- `access_document_version_user` - Standard users can read/write/create versions (no delete)
- `access_document_version_manager` - System users have full CRUD permissions

## Views

- **List View**: Quick overview of versions (name, number, state, author, date, file)
- **Form View**: Full version details with approval buttons, file info, and chatter
- **Wizard Form**: Clean upload interface for new versions
- **Menu Item**: "Document Versions" added to Mail menu for quick access

## Database Schema

No additional tables are created; the module uses:
- `document_version` table for version tracking
- `ir.attachment` for file storage
- Standard Odoo fields for users, dates, and relationships

## Compatibility

- **Odoo Version**: 18.0 (Community & Enterprise)
- **License**: LGPL-3.0
- **Dependencies**: mail, base

## Notes for Developers

### Extending the Module

To add custom logic on version approval:

```python
class DocumentVersion(models.Model):
    _inherit = 'document.version'

    def action_approve(self):
        super().action_approve()
        # Your custom logic here
```

### Custom States

Add new states by extending the STATE_SELECTION in `models/document_version.py`.

### Integration with Workflows

Document versions support full Odoo chatter integration, so version approvals can trigger notifications and appear in team feeds automatically.

## Support

For issues, feature requests, or support: https://amadio.io/support

---

**Author**: AMADIO
**Website**: https://amadio.io
**Price**: EUR 49.00
