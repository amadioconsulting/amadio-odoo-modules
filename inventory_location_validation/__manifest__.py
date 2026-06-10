{
    'name': 'Real-Time Inventory Location Validation',
    'summary': 'Enforce inventory location rules by product category with real-time validation, compliance alerts, and warehouse stock picking routing for Odoo 18.',
    'description': '''
Real-Time Inventory Location Validation

WHAT IT DOES
The Real-Time Inventory Location Validation module ensures that warehouse operators cannot
move products to non-compliant storage locations. It validates destination locations against
configurable rules tied to product categories in real-time during stock picking operations
(deliveries, receipts, internal transfers). Violations trigger warnings or blocks depending
on your configuration.

KEY FEATURES
• Category-Based Rules: Define location restrictions per product category, not per product
• Flexible Actions: Choose between warning alerts (inform user) or hard blocks (prevent validation)
• Manager Configuration: Intuitive Inventory > Configuration > Location Rules menu for rule setup
• Real-Time Validation: Checks triggered automatically during stock picking validation
• Batch Review: Wizard dialog shows all violations at once for informed confirmation
• Audit Trail: Notes field on rules enables compliance documentation and change tracking

WHO NEEDS IT
1. Multi-warehouse operations with strict product placement policies (pharma, food, compliance zones)
2. Quality assurance teams enforcing storage environment requirements (temperature, humidity constraints)
3. Logistics businesses managing hazmat or restricted category inventory across facility zones

TECHNICAL DETAILS
The module extends Odoo's stock.picking model with location validation hooks. It introduces
a new model (stock.location.rule) where managers define location restrictions by category.
When a user clicks "Validate" on a picking, the module loops through all move lines, checks
each destination location against active rules, and either warns or blocks based on configuration.
A confirmation wizard allows users to acknowledge and override warnings if needed. The feature
integrates seamlessly with Odoo's standard picking workflow and respects user permissions via
manager/user role separation.
    ''',
    'version': '18.0.1.0.2',
    'category': 'Inventory/Warehouse',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'depends': ['stock'],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_location_rule_views.xml",
        "views/stock_location_validation_wizard_views.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 89.00,
    'currency': 'EUR',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
}
