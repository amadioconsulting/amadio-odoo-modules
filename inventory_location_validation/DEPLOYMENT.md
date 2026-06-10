# Deployment Guide for inventory_location_validation

## Pre-Deployment Checklist

- [ ] Odoo 18.0 instance is running and accessible
- [ ] `stock` module is installed
- [ ] Admin user credentials available
- [ ] Backup of the production database exists (recommended)
- [ ] Module dependencies resolved (`stock` module pre-installed)

## Installation Steps

### 1. Copy Module Files

```bash
# Copy the entire module to your Odoo addons directory
cp -r inventory_location_validation /path/to/odoo/addons/
```

**Path Examples:**
- Community Edition: `/odoo/addons/`
- Enterprise Edition: `/odoo/enterprise/addons/`
- Custom Addons: `/var/lib/odoo/addons/custom/`

### 2. Restart Odoo Service

```bash
# Stop the Odoo service
sudo systemctl stop odoo

# Start the Odoo service
sudo systemctl start odoo
```

Or if running via Docker:
```bash
docker-compose restart odoo
```

### 3. Update App List (Odoo UI)

1. Log in as an Administrator
2. Navigate to **Apps** (or **Modules** in older UI)
3. Click the **Update Apps List** button (or Refresh icon)
4. Wait for the update to complete

### 4. Install the Module

**Method 1: Via UI (Recommended for Non-Developers)**
1. Navigate to **Apps** > **Apps**
2. Search for "Real-Time Inventory Location Validation"
3. Click the module card
4. Click **Install** button
5. Confirm the installation

**Method 2: Via Command Line (For Developers)**

```bash
# Connect to the Odoo container or server
cd /path/to/odoo

# Install the module in development mode
odoo-bin -d database_name -u inventory_location_validation --without-demo=all
```

**Method 3: Via Odoo Shell (For Automation)**

```bash
python3
>>> import os; os.environ['ODOO_RC'] = '/etc/odoo/odoo.conf'
>>> from odoo.api import Environment
>>> from odoo.modules import get_module_path
>>> import odoo
>>> odoo.cli.main(['', '-d', 'your_database', '-u', 'inventory_location_validation', '--stop-after-init'])
```

## Post-Installation Verification

### Check Module Status

1. Navigate to **Apps** > **Apps**
2. Remove the "Installed" filter (if present)
3. Search for "inventory_location_validation"
4. Verify the module shows as **Installed** (green checkmark)

### Verify Menu Creation

1. Navigate to **Inventory** > **Configuration**
2. Confirm **Location Rules** menu item is visible
3. Click on it to open the empty location rules list

### Test Wizard Creation

1. Create a simple test rule:
   - Navigate to **Inventory > Configuration > Location Rules**
   - Click **Create**
   - Select a Product Category (e.g., "All")
   - Select a Stock Location (e.g., "Stock")
   - Set Action: "Warn"
   - Click **Save**

2. Create a test stock picking:
   - Go to **Inventory > Operations > Receipts** (or another picking type)
   - Create a new receipt
   - Add a product from the selected category
   - Set the destination to the configured restricted location
   - The warning banner should appear on the form
   - Click **Validate** to trigger the wizard

## Configuration Setup (Post-Installation)

### 1. Create Location Rules

```
Example: Pharmaceutical Storage Compliance
- Product Category: "Medications"
- Disallowed Location: "General Storage"
- Action: "Block"
- Note: "Medications must be stored in climate-controlled locations only"
```

### 2. Assign Proper Permissions

By default, the module uses:
- **stock.group_stock_user**: View access
- **stock.group_stock_manager**: Full access

If you have custom groups:
1. Go to **Settings > Users & Companies > Groups**
2. Edit your custom groups to include the appropriate access levels

### 3. Document Rules

Maintain a record of all location rules for compliance:
```
Location Rule Audit Log:
1. Created: 2024-01-15 | Category: Cold Chain | Block from: Room Temp | Reason: Thermal stability
2. Created: 2024-02-10 | Category: Hazmat | Block from: Enclosed Storage | Reason: Ventilation required
```

## Troubleshooting Deployment Issues

### Module not appearing in app list

**Solution:**
```bash
# Update module list from CLI
odoo-bin -d database_name -u base --without-demo=all

# Clear browser cache and hard refresh
# Ctrl+Shift+R (Chrome/Firefox) or Cmd+Shift+R (Mac)
```

### "stock" module not found

**Solution:**
Ensure the stock module is installed:
```bash
odoo-bin -d database_name -u stock --without-demo=all
```

### Permission denied errors

**Solution:**
Verify file permissions:
```bash
sudo chown -R odoo:odoo /path/to/addons/inventory_location_validation/
sudo chmod -R 755 /path/to/addons/inventory_location_validation/
```

### Database migration issues

**Solution:**
Run module update with demo data removed:
```bash
odoo-bin -d database_name -u inventory_location_validation --without-demo=all
```

## Rollback Procedure

If you need to uninstall the module:

1. **Via UI:**
   - Navigate to **Apps > Apps**
   - Search for the module
   - Click the module card
   - Click **Uninstall** button
   - Confirm

2. **Via CLI:**
   ```bash
   # Remove the module directory
   rm -rf /path/to/addons/inventory_location_validation/

   # Restart Odoo
   sudo systemctl restart odoo
   ```

3. **Data Cleanup (Optional):**
   ```sql
   -- Remove all location rules (optional)
   DELETE FROM stock_location_rule;
   ```

## Performance Considerations

### Rule Check Optimization

The module checks all rules on every picking validation. For instances with 1000+ rules:

**Optimization Strategy:**
- Keep rules **Active = True** only for currently enforced rules
- Archive old rules instead of deleting them
- Use a single restrictive rule per location when possible

### Database Index

Consider adding an index for faster rule lookups:

```sql
CREATE INDEX idx_location_rule_category_location
ON stock_location_rule(product_category_id, location_id)
WHERE active = true;
```

## Monitoring & Maintenance

### Log Violations

Create a scheduled action to log violations:

```python
# In a custom module
@api.model
def log_location_violations(self):
    pickings = self.env['stock.picking'].search([
        ('state', 'in', ['assigned', 'in_progress']),
        ('has_location_violations', '=', True),
    ])
    # Log to external system or file
```

### Regular Audits

Schedule weekly reviews:
1. Check rule usage (which rules are being triggered)
2. Review blocked pickings (escalated cases)
3. Archive unused rules
4. Update documentation

## Support & Contact

For deployment assistance or issues:
- **Documentation**: See README.md
- **Author**: AMADIO
- **Website**: https://amadio.io

## Version Compatibility

- **Odoo Version**: 18.0 (required)
- **Python Version**: 3.8+ (recommended)
- **Database**: PostgreSQL 13+ (recommended)

## License

LGPL-3 - See LICENSE file in module directory
