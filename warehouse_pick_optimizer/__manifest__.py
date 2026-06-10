{
    'name': 'Warehouse Pick Path Optimizer',
    'version': '18.0.1.0.2',
    'category': 'Inventory/Warehouse',
    'summary': 'Optimize pick paths by reordering move lines by shelf location sequence for faster warehouse picking and efficient pick route planning.',
    'description': '''
Warehouse Pick Path Optimizer for Odoo 18.0

WHAT IT DOES
The Warehouse Pick Path Optimizer solves a common warehouse inefficiency: pickers waste time walking back and forth because Odoo's default pick list is ordered by sale order line, not by physical shelf location. This module adds an "Optimize Pick Path" button to transfer orders (stock.picking) that intelligently reorders move lines by bin/shelf location, then generates a clean, optimized pick list PDF for faster picking operations.

KEY FEATURES
• Optimize Pick Path button on picking forms — automatically reorders move lines by location sequence
• Custom location sequence field — admins set pick_sequence on storage locations (Physical > Configuration > Pick Sequences)
• Optimized pick list PDF report — shows picking reference, date, operator, then moves in location order with product name, lot/serial, quantity, source and destination locations, and barcode
• Location sequence editor — tree view to bulk-edit pick_sequence on storage locations in hierarchical order
• Pick sequence menu — dedicated Inventory > Configuration > Pick Sequences menu for managing location sequences
• Supports all picking types — works with outgoing and internal transfers
• Barcode integration — displays product barcodes on pick list for barcode-based operations
• Odoo 18.0 native — uses modern QWeb PDF reporting and native Odoo 18 API

WHO NEEDS IT
• Large warehouses with multiple pick zones and inefficient picking routes
• E-commerce businesses with high order volume and complex fulfillment workflows
• Third-party logistics (3PL) providers needing optimized warehouse operations
• Businesses implementing lean warehouse practices and seeking to reduce picker travel time

TECHNICAL DETAILS
This module extends stock.location and stock.picking models:
- Adds pick_sequence (Integer) field to stock.location for custom location ordering
- Implements action_optimize_pick_path() method to reorder stock.move.line records
- Generates optimized pick list PDF report via QWeb template
- Provides location sequence tree view editor for bulk management
- Compatible with Odoo 18.0 standard and custom warehouse configurations
- No modifications to core Odoo picking logic — purely additive enhancement
    ''',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'price': 79.00,
    'currency': 'EUR',
    'depends': ['stock'],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "report/pick_list_report.xml",
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'application': False,
}
