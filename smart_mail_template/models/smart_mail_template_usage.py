from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SmartMailTemplateUsage(models.Model):
    _name = 'smart.mail.template.usage'
    _description = 'Smart Mail Template Usage Tracking'
    _order = 'last_used desc'
    _rec_name = 'template_id'

    template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        required=True,
        ondelete='cascade',
        index=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True
    )
    use_count = fields.Integer(
        string='Usage Count',
        default=0,
        help='Number of times this template has been used by this user'
    )
    last_used = fields.Datetime(
        string='Last Used',
        help='Timestamp of last usage'
    )
    created_date = fields.Datetime(
        string='Created',
        readonly=True,
        default=lambda self: fields.Datetime.now()
    )

    _sql_constraints = [
        (
            'unique_template_user',
            'UNIQUE(template_id, user_id)',
            'Each user can only have one usage record per template'
        ),
    ]

    @api.model
    def record_usage(self, template_id, user_id):
        """
        Record or update usage of a template by a user.
        Called whenever a template is applied in the mail composer.
        """
        if not template_id or not user_id:
            return None

        usage = self.search(
            [('template_id', '=', template_id), ('user_id', '=', user_id)],
            limit=1
        )

        if usage:
            usage.write({
                'use_count': usage.use_count + 1,
                'last_used': fields.Datetime.now(),
            })
        else:
            usage = self.create({
                'template_id': template_id,
                'user_id': user_id,
                'use_count': 1,
                'last_used': fields.Datetime.now(),
            })

        return usage

    @api.model
    def get_recently_used(self, user_id, limit=5, days=30):
        """
        Get recently used templates for a user within the last N days.
        """
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        return self.search(
            [
                ('user_id', '=', user_id),
                ('last_used', '>=', cutoff_date),
            ],
            order='last_used desc',
            limit=limit
        )

    @api.model
    def get_frequently_used(self, user_id, limit=5):
        """
        Get most frequently used templates for a user (by use_count).
        """
        return self.search(
            [('user_id', '=', user_id)],
            order='use_count desc',
            limit=limit
        )

    def name_get(self):
        result = []
        for record in self:
            name = f'{record.template_id.name} (used {record.use_count}x by {record.user_id.name})'
            result.append((record.id, name))
        return result
