{
    'name': 'Analytic Budget Alert & Variance Monitor',
    'version': '18.0.1.0.2',
    'summary': 'Set warn/block thresholds on analytic accounts — get email alerts when spending approaches budget and block over-budget postings before they happen.',
    'category': 'Accounting/Accounting',
    'depends': [
        'analytic',
        'account',
        'mail',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/analytic_account_views.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'currency': 'EUR',
    'price': 59.00,
    'support': 'support@amadio.io',
    'description': '''
Analytic Budget Alert & Variance Monitor

A powerful budget control module for Odoo accounting that prevents overspending on analytic accounts
before it happens. Set warn and block thresholds, get real-time email alerts, and control spending
with customizable budget periods.

Key Features:
- Threshold Configuration: Set warn % and block % for each analytic account
- Email Alerts: Automatic notifications when spending approaches your budget
- Block Overspending: Prevent posting of transactions that exceed block threshold
- Budget Periods: Support for monthly, quarterly, annual, and custom date ranges
- Percent-Spent Dashboard: Visual progress tracking on analytic account forms
- Activity Log: Track all budget-related events and alerts
- Multi-recipient Alerts: Configure who receives budget warning emails
- Real-time Monitoring: Automatic checks on vendor bills and expense entries

Use Cases:
- Nonprofits managing project budgets
- Project-based organizations tracking analytic spending
- Churches and ministries controlling departmental costs
- Small businesses managing internal project allocations
- Any organization needing granular budget control

How it Works:
1. Enable budgets on analytic accounts and set your thresholds
2. Configure budget amounts, periods, and alert recipients
3. System automatically monitors spending on the account
4. Alerts fire when warn threshold is reached
5. Transactions are blocked if they would exceed the block threshold

The module integrates seamlessly with Odoo's native analytic account system and respects
your existing accounting controls and workflows.
    ''',
}
