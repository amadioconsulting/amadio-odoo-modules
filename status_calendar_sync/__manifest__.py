{
    'name': 'Status-to-Calendar Automation',
    'version': '18.0.1.0.2',
    'summary': 'Automatically create calendar events when records change status or stage—workflow automation for service businesses.',
    'description': """Status-to-Calendar Automation for Odoo
=====================================

WHAT IT DOES
-----------
When a record in any Odoo model (Sales Orders, Projects, Tasks, Opportunities, etc.)
transitions to a specific status or stage, this module instantly creates a calendar event
with customizable details. No coding required.

KEY FEATURES
-----------
• Trigger calendar events on any status/stage change
• Configurable event templates with record data placeholders
• Automatic event scheduling (e.g., 3 days after trigger)
• Flexible assignment: current user, responsible user, or all followers
• Support for multiple calendar event types
• Per-rule activation/deactivation without deletion
• Server-side automation—no manual workflow configuration needed
• Fully Odoo 18.0 native using base.automation integration

WHO NEEDS THIS
-----------
Service Companies: Create "Follow-up Call" events when sales orders are confirmed
Project Teams: Schedule check-in meetings when tasks move to "In Progress"
Support Departments: Auto-schedule review calls when tickets are resolved

TECHNICAL DETAILS
-----------
Built on Odoo 18.0 calendar and base_automation frameworks, this module:
- Provides calendar.sync.rule model for rule definition
- Uses server actions (ir.actions.server) for reliable model-agnostic triggering
- Supports dynamic event naming via {record_name} and {record_url} placeholders
- Assigns events based on configured user fields on source records
- Includes full audit trail integration with mail.thread
- Respects Odoo security model—events created with record-owning user context

For AMADIO customers: P09 standard configuration, fully white-label ready.
""",
    'category': 'Productivity',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'price': 69.00,
    'currency': 'EUR',
    'depends': [
        'calendar',
        'base_automation',
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_data.xml",
        "views/calendar_sync_rule_views.xml",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
