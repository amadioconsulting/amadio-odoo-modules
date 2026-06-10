{
    'name': 'SOP Checklist Builder',
    'version': '18.0.1.0.2',
    'summary': 'Create reusable SOP checklist templates and launch them on any Odoo record — track step-by-step completion with timestamps, responsible users, and workflow blocking on critical steps.',
    'category': 'Project',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'price': 69.00,
    'currency': 'EUR',
    'depends': ['mail', 'base'],
    "data": [
        "security/ir.model.access.csv",
        "views/sop_checklist_views.xml",
        "views/sop_template_views.xml",
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'description': '''
SOP Checklist Builder: Complete Process Control

============================================

FEATURES
========

• Template Library
  - Create unlimited SOP templates
  - Store templates by category and code
  - Reusable across any Odoo model

• One-Click Launch
  - Launch any SOP template on a record (sale order, project, picking, etc.)
  - Template steps automatically copied to a new checklist instance
  - Link remains persistent on the record

• Step-by-Step Completion
  - Mark steps done individually with timestamps
  - Records who completed each step
  - Optional evidence attachments for audit compliance
  - Notes field for step-level comments

• Critical Step Blocking
  - Mark steps as critical to block workflow
  - Completion warnings until all critical steps done
  - Prevents premature record state changes
  - Full audit trail

• Progress Tracking
  - Real-time completion percentage
  - Step counts (done / total)
  - Visual progress bar in forms
  - Completion audit trail with dates and users

• Any Model Support
  - Launch checklists on sales orders, projects, pickings, invoices, etc.
  - Works with custom models too
  - Model filtering per template (optional)

• Print-Ready Checklists
  - Print checklist with logo and completion status
  - Include dates and responsible users
  - Export completion audit trail

PERFECT FOR
===========

• Employee Onboarding
  - Multi-step onboarding process
  - Critical document sign-offs
  - Equipment handover verification

• Client Onboarding
  - Structured intake process
  - Evidence attachments (contracts, IDs, etc.)
  - Completion milestone tracking

• Product Launch
  - Pre-launch quality gates
  - Cross-team coordination
  - Critical blocking on unfinished steps

• Order Fulfillment
  - Quality control checklist
  - Packing verification
  - Final inspection signoff

• Safety Inspections
  - Daily/weekly safety audits
  - Evidence photo attachments
  - Critical hazard blocking

• IT Deployment
  - Server setup verification
  - Security checklist completion
  - Rollback decision points

WORKS WITH
==========

Odoo 18.0
Python 3.10+
PostgeSQL 13+
    ''',
}
