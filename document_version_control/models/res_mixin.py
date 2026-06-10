from odoo import api, fields, models


class DocumentVersionMixin(models.AbstractModel):
    """
    Mixin to add document versioning capabilities to any Odoo model.
    Provides one2many relationship to document versions and helper methods.
    """
    _name = 'document.version.mixin'
    _description = 'Document Version Mixin'

    document_version_ids = fields.One2many(
        'document.version',
        compute='_compute_document_versions',
        string='Document Versions',
        help='All versioned documents attached to this record',
    )
    document_version_count = fields.Integer(
        string='Document Count',
        compute='_compute_document_versions',
        help='Total number of versioned documents attached to this record',
    )

    @api.depends('id')
    def _compute_document_versions(self):
        """Compute the document versions for this record."""
        DocumentVersion = self.env['document.version']
        for record in self:
            if record.id:
                versions = DocumentVersion.search([
                    ('res_model', '=', record._name),
                    ('res_id', '=', record.id),
                ])
                record.document_version_ids = versions
                record.document_version_count = len(versions)
            else:
                record.document_version_ids = False
                record.document_version_count = 0

    def action_open_document_versions(self):
        """Open a window action showing all document versions for this record."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Document Versions',
            'res_model': 'document.version',
            'view_mode': 'tree,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }

    def action_open_upload_wizard(self):
        """Open the document version upload wizard for this record."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Document Version',
            'res_model': 'document.version.upload.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
