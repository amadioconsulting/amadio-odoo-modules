from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime


class DocumentVersion(models.Model):
    """
    Manages versioned document attachments for any Odoo record.
    Supports version tracking, approval workflows, and automatic superseding of older versions.
    """
    _name = 'document.version'
    _description = 'Document Version'
    _inherit = ['mail.thread']
    _order = 'date DESC'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('superseded', 'Superseded'),
        ('rejected', 'Rejected'),
    ]

    # Core fields
    name = fields.Char(
        string='Document Title',
        required=True,
        tracking=True,
        help='The name or title of the versioned document',
    )
    version_number = fields.Char(
        string='Version Number',
        required=False,
        tracking=True,
        help='Version identifier (e.g., "1.0", "2.3", "Rev-A")',
    )
    res_model = fields.Char(
        string='Model',
        required=True,
        help='The model of the record this version belongs to',
    )
    res_id = fields.Integer(
        string='Record ID',
        required=True,
        help='The ID of the record this version belongs to',
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade',
        help='The actual file attachment',
    )

    # Convenience fields from attachment
    file_name = fields.Char(
        string='File Name',
        compute='_compute_file_info',
        store=True,
        help='The name of the attached file',
    )
    file_size = fields.Integer(
        string='File Size (bytes)',
        compute='_compute_file_info',
        store=True,
        help='Size of the file in bytes',
    )

    # State and approval
    state = fields.Selection(
        STATE_SELECTION,
        string='State',
        default='draft',
        required=True,
        tracking=True,
        help='Current state of this version',
    )
    approval_required = fields.Boolean(
        string='Approval Required',
        default=False,
        tracking=True,
        help='If checked, this version must be approved before becoming active',
    )
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True,
        help='The user who approved this version',
    )

    # Metadata
    author_id = fields.Many2one(
        'res.users',
        string='Author',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        help='The user who uploaded this version',
    )
    date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='When this version was uploaded',
    )
    notes = fields.Text(
        string='Change Notes',
        tracking=True,
        help='Notes about changes in this version',
    )
    previous_version_id = fields.Many2one(
        'document.version',
        string='Previous Version',
        help='Link to the prior version of this document',
        ondelete='set null',
    )

    # Computed field
    version_label = fields.Char(
        string='Version Label',
        compute='_compute_version_label',
        store=False,
        help='Human-readable version label',
    )

    @api.depends('version_number', 'name')
    def _compute_version_label(self):
        """Compute a human-readable version label."""
        for record in self:
            if record.version_number:
                record.version_label = f'v{record.version_number} — {record.name}'
            else:
                record.version_label = record.name

    @api.depends('attachment_id')
    def _compute_file_info(self):
        """Compute file name and size from the attachment."""
        for record in self:
            if record.attachment_id:
                record.file_name = record.attachment_id.name
                record.file_size = record.attachment_id.file_size
            else:
                record.file_name = False
                record.file_size = 0

    @api.model_create_multi
    def create(self, vals_list):
        """Create new document versions and handle previous version tracking."""
        records = super().create(vals_list)
        for record in records:
            # Find if there's a previous active version for the same name/model/record
            previous = self.search([
                ('name', '=', record.name),
                ('res_model', '=', record.res_model),
                ('res_id', '=', record.res_id),
                ('id', '!=', record.id),
                ('state', '!=', 'superseded'),
                ('state', '!=', 'rejected'),
            ], order='date DESC', limit=1)
            if previous:
                record.previous_version_id = previous.id
        return records

    def action_approve(self):
        """Approve this version and set it as active, superseding any previous active version."""
        for record in self:
            if record.state == 'rejected':
                raise UserError('Cannot approve a rejected version.')

            # Find and supersede the previous active version for this doc name
            previous_active = self.search([
                ('name', '=', record.name),
                ('res_model', '=', record.res_model),
                ('res_id', '=', record.res_id),
                ('state', '=', 'active'),
                ('id', '!=', record.id),
            ])
            if previous_active:
                previous_active.write({
                    'state': 'superseded',
                })

            record.write({
                'state': 'active',
                'approved_by_id': self.env.user.id,
            })

    def action_reject(self):
        """Reject this version."""
        for record in self:
            record.write({
                'state': 'rejected',
                'approved_by_id': self.env.user.id,
            })

    def action_supersede(self):
        """Manually mark this version as superseded."""
        self.write({'state': 'superseded'})

    def unlink(self):
        """Prevent deletion of versions; instead mark them as superseded."""
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    f'Cannot delete {record.version_label}. Versions are archived, not deleted. '
                    'Please mark it as superseded if needed.'
                )
        return super().unlink()
