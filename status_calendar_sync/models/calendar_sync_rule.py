from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class CalendarSyncRule(models.Model):
    """
    Defines rules for automatically creating calendar events when records
    change status or stage. Each rule monitors a specific field on a model
    and creates a calendar event when that field matches a trigger value.
    """
    _name = 'calendar.sync.rule'
    _description = 'Status-to-Calendar Sync Rule'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of rule evaluation'
    )
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Display name for this sync rule (e.g., "SO Confirm → Follow-up Call")'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Activate/deactivate this rule without deletion'
    )

    # Source model and field configuration
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Source Model',
        required=True,
        help='Model on which to monitor status/stage changes'
    )
    model_name = fields.Char(
        related='model_id.model',
        string='Model Name',
        store=False,
        readonly=True
    )
    trigger_field = fields.Char(
        string='Trigger Field',
        required=True,
        help='Field name to monitor (e.g., "state", "stage_id")'
    )
    trigger_value = fields.Char(
        string='Trigger Value',
        required=True,
        help='Value to match (e.g., "sale" for state, "3" for stage_id integer ID)'
    )

    # Calendar event creation parameters
    event_name_template = fields.Char(
        string='Event Name Template',
        required=True,
        default='Follow-up: {record_name}',
        help='Event title. Use {record_name} and {record_url} placeholders'
    )
    event_delay_days = fields.Integer(
        string='Event Delay (days)',
        default=0,
        help='Number of days to delay event creation after trigger'
    )
    event_duration = fields.Float(
        string='Event Duration (hours)',
        default=1.0,
        help='Duration of created calendar event in hours'
    )
    event_categ_id = fields.Many2one(
        comodel_name='calendar.event.type',
        string='Event Type/Category',
        help='Calendar event type (color coding)'
    )

    # User assignment configuration
    assign_to = fields.Selection(
        selection=[
            ('current_user', 'Current User (who triggered the change)'),
            ('responsible_user', 'Responsible User (from source record field)'),
            ('all_followers', 'All Followers (from mail.followers)'),
        ],
        string='Assign Event To',
        required=True,
        default='current_user',
        help='Who should the calendar event be assigned to'
    )
    responsible_field = fields.Char(
        string='Responsible User Field',
        help='Field name on source model for responsible user (e.g., "user_id" for Sales, "project_id.user_id" for Tasks)',
    )

    # Event description
    description_template = fields.Text(
        string='Event Description Template',
        help='Event description. Use {record_name} and {record_url} placeholders'
    )

    # Server action reference (created automatically)
    server_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Linked Server Action',
        readonly=True,
        help='Automatically created base.automation server action for this rule'
    )

    @api.constrains('trigger_field')
    def _check_trigger_field(self):
        """Validate that trigger_field exists on the target model."""
        for record in self:
            if not record.model_id:
                continue

            model = self.env[record.model_id.model]
            if not hasattr(model, '_fields') or record.trigger_field not in model._fields:
                raise ValidationError(
                    f"Field '{record.trigger_field}' does not exist on model '{record.model_id.name}'"
                )

    @api.constrains('responsible_field', 'assign_to')
    def _check_responsible_field(self):
        """Validate responsible_field if assign_to is 'responsible_user'."""
        for record in self:
            if record.assign_to == 'responsible_user' and not record.responsible_field:
                raise ValidationError(
                    "Please specify a 'Responsible User Field' when using 'Responsible User' assignment"
                )

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        """Create rules and generate corresponding server actions."""
        records = super().create(vals_list)
        for record in records:
            if record.active:
                record._create_server_action()
        return records

    def write(self, vals):
        """Update rules and regenerate server actions if configuration changed."""
        result = super().write(vals)

        # Regenerate server action if key fields changed
        if any(field in vals for field in [
            'model_id', 'trigger_field', 'trigger_value', 'active',
            'event_name_template', 'event_delay_days', 'event_duration',
            'event_categ_id', 'assign_to', 'responsible_field', 'description_template'
        ]):
            for record in self:
                if record.server_action_id:
                    record.server_action_id.unlink()
                    record.server_action_id = False

                if record.active:
                    record._create_server_action()

        return result

    def unlink(self):
        """Delete rules and clean up server actions."""
        for record in self:
            if record.server_action_id:
                record.server_action_id.unlink()
        return super().unlink()

    def _create_server_action(self):
        """
        Create or update a base.automation (ir.actions.server) record
        that will trigger calendar event creation on write for the configured model.
        """
        self.ensure_one()

        if not self.model_id:
            return

        # Delete existing action if present
        if self.server_action_id:
            self.server_action_id.unlink()

        # Create new server action with model-specific name
        action_name = f"[SYNC] {self.name}"

        server_action = self.env['ir.actions.server'].create({
            'name': action_name,
            'model_id': self.model_id.id,
            'state': 'code',
            'code': self._get_server_action_code(),
            'binding_model_id': self.model_id.id,
            'binding_type': 'action',
        })

        self.server_action_id = server_action.id
        _logger.info(f"Created server action {server_action.id} for rule {self.id} ({self.name})")

    def _get_server_action_code(self):
        """Generate Python code for server action that creates calendar events."""
        return f"""
# Auto-generated calendar sync code for rule ID {self.id}
rule = env['calendar.sync.rule'].browse({self.id})
if rule and rule.active:
    for record in records:
        rule._trigger_calendar_event_if_matched(record)
"""

    def _trigger_calendar_event_if_matched(self, record):
        """
        Check if the given record matches this rule's trigger condition,
        and if so, create a calendar event.
        """
        self.ensure_one()

        if not self.active or not self.model_id:
            return

        # Get the field value from the record
        try:
            field_value = record[self.trigger_field]
        except KeyError:
            _logger.warning(
                f"Field {self.trigger_field} not found on record {record.id} of {record._name}"
            )
            return

        # Compare trigger value (handle both string and many2one IDs)
        trigger_matched = False
        if isinstance(field_value, models.BaseModel):
            # Many2one field: compare ID
            trigger_matched = str(field_value.id) == str(self.trigger_value)
        else:
            # Regular field: compare string representation
            trigger_matched = str(field_value) == str(self.trigger_value)

        if trigger_matched:
            self._create_calendar_event(record)

    def _create_calendar_event(self, source_record):
        """Create a calendar event based on this rule and the source record."""
        self.ensure_one()

        try:
            # Prepare event name
            event_name = self.event_name_template.format(
                record_name=source_record.name if hasattr(source_record, 'name') else str(source_record.id),
                record_url=f"#model={source_record._name}&id={source_record.id}" if source_record.id else "",
            )
        except (KeyError, AttributeError) as e:
            _logger.warning(f"Error formatting event name: {e}")
            event_name = f"Event for {source_record.name}"

        # Prepare event description
        event_description = ""
        if self.description_template:
            try:
                event_description = self.description_template.format(
                    record_name=source_record.name if hasattr(source_record, 'name') else str(source_record.id),
                    record_url=f"#model={source_record._name}&id={source_record.id}" if source_record.id else "",
                )
            except (KeyError, AttributeError):
                pass

        # Calculate event start datetime
        start_datetime = fields.Datetime.now() + timedelta(days=self.event_delay_days)
        end_datetime = start_datetime + timedelta(hours=self.event_duration)

        # Determine which user(s) to assign the event to
        partner_ids = []
        if self.assign_to == 'current_user':
            # Current user (who made the write)
            partner_ids = [self.env.user.partner_id.id]

        elif self.assign_to == 'responsible_user':
            # Field-based responsible user
            if self.responsible_field:
                try:
                    # Handle dot notation (e.g., "project_id.user_id")
                    field_parts = self.responsible_field.split('.')
                    target_obj = source_record
                    for part in field_parts:
                        if hasattr(target_obj, part):
                            target_obj = target_obj[part]
                        else:
                            raise AttributeError(f"Field {part} not found")

                    if target_obj and hasattr(target_obj, 'partner_id'):
                        partner_ids = [target_obj.partner_id.id]
                    elif target_obj:
                        _logger.warning(f"Target object {target_obj} has no partner_id")
                except (AttributeError, TypeError) as e:
                    _logger.warning(f"Error resolving responsible user field: {e}")

        elif self.assign_to == 'all_followers':
            # All followers of the source record
            if hasattr(source_record, 'message_follower_ids'):
                partner_ids = source_record.message_follower_ids.mapped('partner_id.id')

        # If no partners found, default to current user
        if not partner_ids:
            partner_ids = [self.env.user.partner_id.id]

        # Create the calendar event
        try:
            event_vals = {
                'name': event_name,
                'start': start_datetime,
                'stop': end_datetime,
                'description': event_description,
                'partner_ids': [(6, 0, partner_ids)],
            }

            if self.event_categ_id:
                event_vals['categ_ids'] = [(6, 0, [self.event_categ_id.id])]

            calendar_event = self.env['calendar.event'].create(event_vals)
            _logger.info(
                f"Created calendar event {calendar_event.id} for rule {self.id} "
                f"on record {source_record._name}/{source_record.id}"
            )
        except Exception as e:
            _logger.error(f"Failed to create calendar event for rule {self.id}: {e}")
