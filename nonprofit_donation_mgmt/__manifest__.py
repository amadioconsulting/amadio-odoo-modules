{
    'name': 'Nonprofit Donation Management',
    'version': '18.0.1.0.2',
    'category': 'Accounting/Accounting',
    'sequence': 1,
    'summary': 'Complete donation tracking, tax receipt generation, and donor management for nonprofits, charities, and religious organizations',
    'description': '''
Nonprofit Donation Management for Odoo 18

WHAT IT DOES
Comprehensive donation management system designed for nonprofits, religious organizations, charities, and faith-based communities. Tracks all donation types (cash, cheque, e-transfer, card), manages donors, organizes donations by campaigns and funds, and generates professional tax receipts in Canadian T4A-ready PDF format. Integrates seamlessly with Odoo Accounting for complete financial visibility, or operates standalone.

KEY FEATURES
• Multi-method donation tracking: cash, cheque, e-transfer, card payments with payment details
• Donor management: complete contact records with donation history and preferences
• Donation campaigns and fund management: organize giving by purpose, track campaign progress toward goals
• Automated tax receipt generation: professional PDF receipts meeting Canadian income tax requirements (T4A-ready)
• Year-end giving statements: generate comprehensive donor summaries by fiscal year for tax documentation
• Accounting integration: optional automatic journal entry creation for donations to track in GL
• Donation sequence numbering: auto-generated reference numbers for all donations
• Donation state workflow: draft → confirmed → receipted tracking
• Search and filtering: find donations by donor, date range, fund, campaign, or payment method
• Dashboard totals: quick overview of donation volume and amounts

WHO NEEDS IT
Churches, synagogues, mosques, temples, and other religious organizations; nonprofits and charitable foundations; community service organizations; schools and educational charities; health and wellness nonprofits; environmental and conservation groups; artistic and cultural organizations; any organization collecting regular donations and requiring tax receipts.

TECHNICAL DETAILS
Models: donation.donation (tracks individual gifts), donation.fund (tracks restricted funds), donation.campaign (tracks fundraising campaigns), donation.year_end_wizard (generates annual donor statements).

Compatibility: Works standalone or alongside Odoo Accounting. Requires Odoo 18.0. Optional integration with account module for GL posting.

Security: Full access control via donation_donation, donation_fund, donation_campaign groups. User-based permissions prevent unauthorized viewing/editing.
    ''',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'price': 149.00,
    'currency': 'EUR',
    'depends': [
        'account',
        'mail',
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/donation_sequence.xml",
        "views/donation_campaign_views.xml",
        "views/donation_donation_views.xml",
        "views/donation_fund_views.xml",
        "views/donation_year_end_wizard_views.xml",
        "report/donation_receipt_report.xml",
    ],
    'demo': [],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
