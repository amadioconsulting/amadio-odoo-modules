import base64
from odoo import api, fields, models
from odoo.exceptions import UserError


class DocumentVersionUploadWizard(models.TransientModel):
    """
    Transient wizard for uploading new document versions.
    Handles file upload, version creation, and automatic superseding of old versions.
    """
    _name = 'document.version.upload.wizard'
    _description = 'Document Version Upload Wizard'

    res_model = fields.Char(
        string='Model',
        required=True,
        help='The model of the record to attach the version to',
    )
    res_id = fields.Integer(
        string='Record ID',
        required=True,
        help='The ID of the record to attach the version to',
    )
    name = fields.Char(
        string='Document Title',
        required=True,
        help='The name or title for this document',
    )
    version_number = fields.Char(
        string='Version Number',
        help='Version identifier (e.g., "1.0", "2.3", "Rev-A")',
    )
    attachment = fields.Binary(
        string='File',
        required=True,
        help='The file to upload',
    )
    attachment_filename = fields.Char(
        string='Filename',
        required=True,
        help='The name of the file',
    )
    notes = fields.Text(
        string='Change Notes',
        help='Notes about changes in this version',
    )
    approval_required = fields.Boolean(
        string='Approval Required',
        default=False,
        help='Require approval before this version becomes active',
    )

    def action_upload(self):
        """
        Create the attachment and document version.
        Automatically supersede the previous active version if approval is not required.
        """
        self.ensure_one()

        if not self.attachment:
            raise UserError('Please select a file to upload.')

        # Create the attachment
        attachment = self.env['ir.attachment'].create({
            'name': self.attachment_filename,
            'datas': self.attachment,
            'res_model': self.res_model,
            'res_id': self.res_id,
        })

        # Determine initial state
        initial_state = 'draft' if self.approval_required else 'active'

        # Create the document version
        version = self.env['document.version'].create({
            'name': self.name,
            'version_number': self.version_number or '',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'attachment_id': attachment.id,
            'notes': self.notes,
            'approval_required': self.approval_required,
            'state': initial_state,
            'author_id': self.env.user.id,
        })

        # If approval is not required, automatically supersede previous active versions
        if not self.approval_required:
            previous_active = self.env['document.version'].search([
                ('name', '=', self.name),
                ('res_model', '=', self.res_model),
                ('res_id', '=', self.res_id),
                ('state', '=', 'active'),
                ('id', '!=', version.id),
            ])
            if previous_active:
                previous_active.write({'state': 'superseded'})

        # Return action to view the new version
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'document.version',
            'res_id': version.id,
            'view_mode': 'form',
            'target': 'current',
        }
