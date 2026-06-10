{
    'name': 'Smart Email Template Selector',
    'version': '18.0.1.0.2',
    'category': 'Discuss',
    'summary': 'Auto-suggest relevant email templates in mail composer — smart template selector for productivity.',
    'description': '''
Smart Email Template Selector
=============================

WHAT IT DOES
The Smart Email Template Selector transforms the email composition experience in Odoo by automatically
surfacing the most relevant templates based on context. Instead of scrolling through hundreds of templates,
users see the 3–5 most relevant suggestions instantly in the mail composer. Click to apply. No more hunting
for the right template.

KEY FEATURES
• Automatic context-aware suggestions: Templates are ranked by relevance to the current model, stage, and partner type
• Recently Used templates: Quick access to the templates you use most, per user
• Intelligent priority system: Configure which templates appear first for each model and stage combination
• Usage tracking: Built-in metrics show which templates are most effective
• Zero configuration in standard use: Works out of the box; customize via Settings > Technical > Email > Smart Template Rules
• Zero disruption: Existing template workflow unchanged; suggestions are optional enhancements

WHO NEEDS IT
Sales teams composing quotes and follow-ups: Instantly apply the right email template for each stage
(proposal, negotiation, closing) without searching.

Support teams responding to tickets: Automatically see FAQs, escalation templates, and closure emails
based on ticket status and priority, reducing response time.

Human Resources managing candidate communications: Quickly select stage-appropriate templates for offer
letters, rejection emails, and onboarding sequences based on hiring workflow position.

TECHNICAL DETAILS
Built on two new data models:
• smart.mail.template.rule — Configures which templates are suggested for which model + stage combinations
• smart.mail.template.usage — Tracks template usage frequency per user for personalized suggestions

The module injects smart suggestions into the standard mail.compose.message wizard, showing template
recommendations in a dedicated "Smart Suggestions" section. Templates are scored by priority and usage
frequency, ensuring the most relevant ones appear at the top. All suggestions are non-intrusive and
fully optional.

Compatible with Odoo 18.0 Community and Enterprise editions.
    ''',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'price': 59.00,
    'currency': 'EUR',
    'depends': ['mail'],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_compose_message_views.xml",
        "views/smart_mail_template_rule_views.xml",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'auto_install': False,
}
