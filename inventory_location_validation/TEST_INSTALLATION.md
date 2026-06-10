# Installation Test Guide

This document describes how to verify that the `inventory_location_validation` module has been installed correctly.

## Pre-Installation Test

Run these checks before installing the module:

### 1. File Integrity

```bash
cd /path/to/inventory_location_validation

# Count files
find . -type f | wc -l
# Expected output: 14 files

# Verify directory structure
ls -la models/ views/ security/ static/description/
# Should all exist

# Check for Python syntax errors
python3 -m py_compile models/*.py
# No output = success
```

### 2. Manifest Validation

```bash
python3
>>> import ast
>>> with open('__manifest__.py') as f: manifest = ast.literal_eval(f.read())
>>> required = ['name', 'version', 'author', 'license', 'depends', 'data', 'installable']
>>> missing = [f for f in required if f not in manifest]
>>> print(f"Missing fields: {missing if missing else 'None'}")
```

### 3. XML Validation

```bash
for file in views/*.xml; do
  python3 -m xml.dom.minidom "$file" > /dev/null && echo "$file: OK" || echo "$file: ERROR"
done
```

## Post-Installation Test (in Odoo)

### Test 1: Module Appears in List

1. Log in as Administrator
2. Go to **Apps > Apps**
3. Remove any installed filters
4. Search for "Real-Time Inventory"
5. **Expected**: Module card appears, shows as "Installed"

### Test 2: Menu Items Created

1. Go to **Inventory > Configuration**
2. **Expected**: "Location Rules" menu item is visible
3. Click on it
4. **Expected**: Empty list view appears with "Create" button

### Test 3: Create a Test Rule

1. Click **Create** in the Location Rules list
2. Fill in:
   - **Product Category**: "All" (or any existing category)
   - **Disallowed Location**: "Stock" (or any warehouse location)
   - **Action**: "Warn"
   - **Note**: "Test rule"
3. Click **Save**
4. **Expected**: Rule appears in the list

### Test 4: Create a Test Picking

1. Go to **Inventory > Operations > Receipts**
2. Click **Create**
3. Set Warehouse and Partner as needed
4. Click **Add a line**
5. Select a product from the category you used in Test 3
6. Set **Destination Location** to the restricted location from Test 3
7. Click **Save**
8. **Expected**: Warning banner appears below the form:
   ```
   Location Validation Warning: This picking has 1 location rule violation(s).
   Review the move destinations before validating.
   ```

### Test 5: Test Warn Action

1. With the test picking from Test 4 still open
2. Click **Validate** button
3. **Expected**: A wizard dialog appears showing:
   - Warning title
   - Product name and destination
   - "Confirm and Validate" button
   - "Cancel" button

### Test 6: Confirm Despite Warning

1. In the wizard dialog from Test 5
2. Click **Confirm and Validate**
3. **Expected**: Wizard closes, picking is validated (state changes to "Done" or "Assigned" depending on type)

### Test 7: Test Block Action

1. Create another location rule:
   - Category: (same as test product)
   - Location: (same as test picking destination)
   - Action: **Block**
   - Save

2. Create another test picking with the same setup as Test 4
3. Click **Validate**
4. **Expected**: Red error box appears with message:
   ```
   Location Validation Error:

   Product: [Product Name]
   Category: [Category Name]
   Destination: [Location Name]
   Reason: [Note from rule]

   This picking cannot be validated due to location restrictions. Contact your manager.
   ```

5. **Expected**: Picking cannot be validated; user must cancel or modify destination

### Test 8: Permission Check

1. Create a non-manager user (Stock User):
   - Go to **Settings > Users & Companies > Users > Create**
   - Set Group: "Stock User" (not Manager)
   - Save

2. Log in as this Stock User
3. Go to **Inventory > Configuration > Location Rules**
4. **Expected**: Rule list is visible (read-only)
5. Try to click **Create**
6. **Expected**: "Create" button is disabled or shows permission error
7. Try to edit an existing rule
8. **Expected**: Edit is blocked

9. Go to a stock picking with violations
10. **Expected**: Warning banner is visible
11. Try to click **Validate**
12. **Expected**: Validation works as normal (warns or blocks based on rules)

### Test 9: Manager Permissions

1. Log in as a Stock Manager user
2. Go to **Inventory > Configuration > Location Rules**
3. **Expected**: "Create" button is available
4. Click **Create**
5. **Expected**: Form opens for creating a new rule
6. Try to edit an existing rule
7. **Expected**: Edit is allowed
8. Try to delete a rule
9. **Expected**: Delete is allowed (with confirmation)

### Test 10: Database Consistency

Run these SQL queries (as database user):

```sql
-- Check if tables exist
SELECT tablename FROM pg_tables WHERE tablename LIKE 'stock_location_rule%';
-- Expected: returns 'stock_location_rule'

-- Check if data was created
SELECT COUNT(*) FROM stock_location_rule;
-- Expected: returns your created rules

-- Check XML ID references
SELECT id, module, name FROM ir_model_data WHERE module = 'inventory_location_validation';
-- Expected: returns views, actions, menu items created
```

## Performance Test

### Test 11: Bulk Rule Performance

1. Create 100+ location rules
2. Create a stock picking with many move lines
3. Click **Validate**
4. **Expected**: Wizard appears within 2 seconds (no timeout)

**Performance Target**: < 500ms for violation check with 1000 rules

## Cleanup Test

### Test 12: Uninstall Module

1. Go to **Apps > Apps**
2. Search for "Real-Time Inventory"
3. Click the module card
4. Click **Uninstall**
5. Confirm uninstallation
6. **Expected**:
   - Menu items disappear
   - Rules can no longer be accessed
   - Picking forms no longer show warning banner
   - Database tables still exist (data preserved)

## Automated Test Suite (Optional)

For developers, run these tests:

```python
# tests/test_location_validation.py
from odoo.tests import TransactionCase

class TestLocationValidation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.stock_rule = self.env['stock.location.rule']

    def test_rule_creation(self):
        """Test basic rule creation"""
        rule = self.stock_rule.create({
            'product_category_id': self.env.ref('product.product_category_all').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'action': 'warn',
            'note': 'Test'
        })
        self.assertIsNotNone(rule.id)

    def test_violation_detection(self):
        """Test that violations are correctly detected"""
        # Create rule
        rule = self.stock_rule.create({
            'product_category_id': ...,
            'location_id': ...,
            'action': 'warn'
        })

        # Create picking that violates rule
        picking = self.env['stock.picking'].create({...})

        # Check for violations
        violations = rule._get_violations(picking.move_ids)
        self.assertGreater(len(violations), 0)

    def test_block_action(self):
        """Test that block action prevents validation"""
        # Create block rule
        rule = self.stock_rule.create({
            'action': 'block',
            ...
        })

        # Try to validate picking
        with self.assertRaises(UserError):
            picking.button_validate()
```

## Rollback Test

### Test 13: Data Preservation

1. Note the count of location rules: `SELECT COUNT(*) FROM stock_location_rule;`
2. Uninstall the module
3. Check if rules still exist in database
4. **Expected**: Rules are preserved in database

5. Reinstall the module
6. Check rule count again
7. **Expected**: Rules are restored and accessible

## Troubleshooting During Testing

### Module doesn't appear in Apps list

- [ ] Restart Odoo service
- [ ] Clear browser cache (Ctrl+Shift+R)
- [ ] Run "Update Apps List" again
- [ ] Check Odoo logs for import errors

### "stock" module not found

- [ ] Ensure stock module is installed: `odoo-bin -d db -u stock`
- [ ] Check manifest depends: should be `['stock']`

### Permission errors on rules

- [ ] Verify user is in "Stock Manager" group
- [ ] Check ir.model.access.csv is loaded correctly
- [ ] Restart Odoo to reload security rules

### Warning banner doesn't appear

- [ ] Verify rule is marked as Active
- [ ] Check product category matches exactly
- [ ] Check location matches exactly
- [ ] Refresh the form (F5)

### Wizard doesn't show on validate

- [ ] Check browser console for JavaScript errors
- [ ] Verify transient model was created: `SELECT * FROM ir_model WHERE model = 'stock.location.validation.wizard';`
- [ ] Check Odoo logs for Python errors

## Test Results Checklist

- [ ] All pre-installation tests pass
- [ ] Module installs without errors
- [ ] Menu items created correctly
- [ ] Can create location rules
- [ ] Warning action works (shows wizard)
- [ ] Block action works (prevents validation)
- [ ] Warn action allows override
- [ ] Stock User sees warnings but cannot manage rules
- [ ] Stock Manager can manage rules
- [ ] Database tables created
- [ ] Uninstall completes cleanly
- [ ] Data is preserved after uninstall

## Sign-off

```
Date: _______________
Tested By: _______________
System: Odoo _____ on _____ (OS/Database)
Status: [ ] PASS  [ ] FAIL

Comments:
_____________________________________________________________
_____________________________________________________________
```

## Support

If tests fail:
1. Check DEPLOYMENT.md for common issues
2. Review Odoo logs: `/var/log/odoo/odoo-server.log`
3. Check database logs
4. Contact AMADIO support: https://amadio.io
