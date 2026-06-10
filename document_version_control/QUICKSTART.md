# Document Version Control - Quick Start Guide

## Installation

1. Copy the module folder to your Odoo addons directory:
   ```bash
   cp -r document_version_control /path/to/odoo/addons/
   ```

2. Restart Odoo service:
   ```bash
   systemctl restart odoo
   ```

3. Open Odoo, go to **Apps**, search for **Document Version Control**, and click **Install**

4. You should now see "Document Versions" in the Mail menu

## Adding Versions to Your Model (5 Minutes)

### Step 1: Edit Your Model

Open `models/my_model.py`:

```python
from odoo import models

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['my.model', 'document.version.mixin']  # Add this line

    name = fields.Char()
    # ... rest of your fields
```

### Step 2: Update Your View

In `views/my_model_views.xml`, add the smart button:

```xml
<form string="My Model">
    <sheet>
        <div class="oe_button_box" name="button_box">
            <!-- Add this button -->
            <button name="action_open_document_versions" type="object"
                    class="oe_stat_button" icon="fa-file-text">
                <field name="document_version_count" widget="statinfo" string="Versions"/>
            </button>
            <!-- Your other buttons here -->
        </div>
        <h1><field name="name"/></h1>
        <!-- ... rest of form -->
    </sheet>
</form>
```

### Step 3: Restart Odoo

```bash
systemctl restart odoo
```

Done! Your model now supports document versioning.

## Using Document Versions

### Upload a New Version

1. Open any record (e.g., a contract, opportunity, SOP)
2. Click the **Versions** smart button
3. Click **Upload Document Version**
4. Fill in:
   - **Document Title**: "Service Agreement"
   - **Version Number**: "1.0" (optional)
   - **File**: Select your file
   - **Change Notes**: "Initial version - ready for review"
   - **Approval Required**: Check if needed
5. Click **Upload Version**

### Approve a Version

1. Open the version record (opens automatically after upload)
2. Click **Approve** button in header
3. Version becomes **Active**, previous version becomes **Superseded**
4. Team sees notification in Chatter

### View Version History

1. Click **Versions** smart button on any record
2. See all versions: status, author, date, file name
3. Click any version to view details

## Common Use Cases

### Contracts

1. Create a contract record
2. Upload initial contract: "Service_Agreement_v1.0"
3. Set "Approval Required" = Yes
4. Manager reviews and approves
5. Next revision uploaded as "Service_Agreement_v1.1"
6. Old version automatically archived

### Standard Operating Procedures (SOPs)

1. Create SOP record for "Email Response Time"
2. Upload SOP v1.0
3. Set as Active (no approval required)
4. When updated, upload v2.0
5. Team always sees current version in list
6. Complete history available for audits

### Proposals

1. Create opportunity
2. Upload proposal "Acme_Proposal_v1.pdf"
3. Send v1 to client
4. Client requests changes
5. Upload "Acme_Proposal_v2.pdf" with notes "Client feedback incorporated"
6. Track which version was sent when

## Approval Workflow

```
User Uploads File with "Approval Required" checked
         ↓
Version created in DRAFT state
         ↓
Manager reviews document
         ↓
Manager clicks APPROVE
         ↓
Version → ACTIVE
Previous active version → SUPERSEDED
All followers notified in Chatter
         ↓
Complete!
```

OR

```
Manager reviews and clicks REJECT
         ↓
Version → REJECTED
User notified to upload new version
```

## Tips & Tricks

### Version Numbering Schemes

Popular schemes:
- **Numeric**: 1.0, 1.1, 1.2, 2.0, 2.1
- **Revision**: Rev-A, Rev-B, Rev-C
- **Date-based**: 2024-03-30-v1, 2024-03-30-v2
- **Mixed**: 1.0-DRAFT, 1.0-FINAL, 1.1-REVIEW

### Tips

1. **Use Clear Names**: "Contract_2024" not "doc123"
2. **Add Change Notes**: "Client requested 30-day payment terms"
3. **Version Numbering**: Helps team understand version progression
4. **Require Approval**: For contracts, policies, SOPs
5. **No Approval**: For internal documents, working drafts

### Bulk Operations

Search for versions by state:
```
List View → Filter → State = "Active"
```

Mark old versions as superseded in bulk (future enhancement).

## Troubleshooting

### "Can't see the Versions button"

1. Ensure module is installed: Go to **Apps**, search "Document Version Control", confirm **Installed**
2. Refresh page (Ctrl+F5)
3. Check that your model inherited `document.version.mixin`
4. Restart Odoo service

### "Version stays in Draft after upload"

This is normal if "Approval Required" was checked. Manager must click **Approve**.

### "Can't delete a version"

By design! Versions are archived, not deleted:
- Mark as **Superseded** if replacing
- Mark as **Rejected** if not needed
- Admins can delete Draft versions only

### "File not showing in version"

1. Check file upload completed (no error message)
2. Refresh page
3. Check ir.attachment was created (admin → Attachments)

## FAQ

**Q: Can I use this on custom models?**
A: Yes! Just add `'document.version.mixin'` to your `_inherit` list.

**Q: What file types are supported?**
A: All! PDF, Word, Excel, images, videos, archives, etc.

**Q: Can I download a version file?**
A: Yes. In the version form, click the attachment filename to download.

**Q: Will old versions be deleted?**
A: No. They're marked as "Superseded" for audit trail. Only Draft versions can be deleted.

**Q: Do I need approval for every version?**
A: No. Check "Approval Required" only when needed. Unchecked versions become Active immediately.

**Q: Can I integrate this with workflows?**
A: Yes. Version states can trigger Odoo automation rules and workflows.

**Q: Storage location for files?**
A: Same as Odoo attachments (local disk, S3, cloud storage, etc.).

**Q: Can I export version history?**
A: Yes. Use Odoo's standard export feature on the versions list.

## Next Steps

1. **Install the module** (see Installation above)
2. **Add to your first model** (see Quick Start above)
3. **Upload a test document** and explore features
4. **Set up approval workflow** for critical documents
5. **Train your team** on version management

## Support & Documentation

- **Full Documentation**: See README.md
- **Technical Details**: See TECHNICAL_OVERVIEW.md
- **Support**: https://amadio.io/support
- **Report Issues**: https://amadio.io/contact

---

**Version**: 18.0.1.0
**Author**: AMADIO
**License**: LGPL-3.0
