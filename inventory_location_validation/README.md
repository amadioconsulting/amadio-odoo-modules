# Real-Time Inventory Location Validation

**Module Name:** `inventory_location_validation`
**Version:** 18.0.1.0.0
**Author:** AMADIO
**License:** LGPL-3
**Odoo Version:** 18.0

## Overview

The Real-Time Inventory Location Validation module enforces warehouse location compliance rules during stock picking operations. It prevents (or warns about) the movement of products to non-compliant storage locations based on configurable rules tied to product categories.

## Features

- **Category-Based Rules**: Define location restrictions per product category, not per product
- **Flexible Actions**: Choose between warning alerts (inform user) or hard blocks (prevent validation)
- **Manager Configuration**: Intuitive Inventory > Configuration > Location Rules menu for rule setup
- **Real-Time Validation**: Checks triggered automatically during stock picking validation
- **Batch Review**: Wizard dialog shows all violations at once for informed confirmation
- **Audit Trail**: Notes field on rules enables compliance documentation and change tracking

## Installation

1. Download the module and place it in your Odoo addons directory
2. Restart the Odoo server
3. Update the app list (Admin > Apps > Update Apps List)
4. Search for "Real-Time Inventory Location Validation" and click Install

## Configuration

### Creating Location Rules

1. Navigate to **Inventory > Configuration > Location Rules**
2. Click **Create** to define a new rule
3. Fill in the following fields:
   - **Product Category**: The category to which the rule applies
   - **Disallowed Location**: The warehouse location where products in this category cannot be moved
   - **Action**:
     - `Warn`: Shows a confirmation dialog when violations are detected
     - `Block`: Prevents validation entirely if violations exist
   - **Note**: Optional explanation (e.g., "Hazmat storage", "Temperature controlled zone")
4. Save the rule

### Example Scenarios

**Scenario 1: Pharma Company**
- Rule: Category "Cold Chain Medications" → Block from "Room Temperature Storage"
- Action: Block (prevents accidental validation to wrong location)

**Scenario 2: Food Warehouse**
- Rule: Category "Allergen Products" → Warn for "General Storage"
- Action: Warn (allows user to confirm intentional placement)

## Usage

### For Warehouse Operators

1. Create or edit a stock picking (receipt, delivery, or internal transfer)
2. Set product move destinations as usual
3. Click **Validate** to proceed
4. If violations exist:
   - **Block violations**: An error message appears; contact your manager to resolve
   - **Warn violations**: A confirmation dialog appears showing all violations; click **Confirm and Validate** to proceed or **Cancel** to adjust destinations

### Banner Indicator

A warning banner appears on the stock picking form if location violations exist:

```
Location Validation Warning: This picking has X location rule violation(s).
Review the move destinations before validating.
```

## Security & Permissions

The module implements role-based access control:

- **Stock Users**: Can view rules and see validation warnings; cannot create/edit rules
- **Stock Managers**: Can create, edit, and delete location rules

Access is controlled via:
- `stock.group_stock_user`: View access to rules
- `stock.group_stock_manager`: Full access to create/edit/delete rules

## Technical Details

### Data Model

**stock.location.rule**
- `product_category_id` (Many2one, required): Product category
- `location_id` (Many2one, required): Disallowed destination location
- `action` (Selection, required): 'warn' or 'block'
- `active` (Boolean): Enable/disable the rule
- `note` (Char): Internal explanation

### Override Points

**stock.picking.button_validate()**
- Intercepts the validate button click
- Checks all move lines against active location rules
- Raises UserError for block violations
- Creates a confirmation wizard for warn violations

**stock.location.validation.wizard** (Transient Model)
- Displays violation details to the user
- Allows confirmation or cancellation
- Bypasses validation check on confirmation

### Database Constraints

- Unique constraint: `UNIQUE(product_category_id, location_id)` prevents duplicate rules

## Troubleshooting

### Issue: Rules not triggering
- Ensure the rule is marked as **Active**
- Verify the product's category matches the rule's category
- Check that the destination location exactly matches the rule's location

### Issue: "Cannot unlink" error when deleting a rule
- The rule may be referenced in a transaction; try again after refreshing the page

### Issue: Wizard appears but confirm button does nothing
- Clear your browser cache and refresh the page
- Ensure you have sufficient permissions (Stock Manager)

## Database Queries for Monitoring

View all active rules:
```sql
SELECT product_category_id, location_id, action, note
FROM stock_location_rule
WHERE active = true
ORDER BY product_category_id;
```

Find violations in recent pickings:
```sql
SELECT sp.name, sm.product_id, sl.name as destination_location
FROM stock_picking sp
JOIN stock_move sm ON sp.id = sm.picking_id
JOIN stock_location sl ON sm.location_dest_id = sl.id
WHERE sp.state IN ('assigned', 'in_progress');
```

## Support & Development

For issues, feature requests, or custom modifications, contact:
- **Website**: https://amadio.io
- **Author**: AMADIO

## Version History

### 18.0.1.0.0 (Initial Release)
- Real-time location validation for stock pickings
- Support for warn and block actions
- Manager-configurable location rules
- Wizard-based violation confirmation
- Full security model integration

## License

This module is licensed under the LGPL-3 License. See LICENSE file for details.
