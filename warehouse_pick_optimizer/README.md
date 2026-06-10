# Warehouse Pick Path Optimizer

Production-ready Odoo 18.0 module for optimizing warehouse picking routes by reordering move lines according to shelf location sequence.

## Module Overview

### Problem Solved
Pickers waste time walking back and forth because Odoo's default pick list is ordered by sale order line, not by physical shelf location. This module intelligently reorders picking operations by warehouse bin/shelf location.

### Solution
- **Optimize Pick Path button** on stock.picking forms automatically reorders move lines by location sequence
- **Pick sequence field** on storage locations allows admins to define the physical picking order
- **Optimized pick list PDF** with products ordered by location sequence for faster, more efficient picking
- **Location sequence editor** provides a hierarchical tree view to manage location sequences

## Installation

1. Place the `warehouse_pick_optimizer` module in your Odoo `addons` directory
2. Update the module list: **Settings > Apps > Update Apps List**
3. Search for "Warehouse Pick Path Optimizer"
4. Click **Install**

## Features

### 1. Optimize Pick Path Button
- Located on stock.picking form (Transfer, Picking operations)
- Visible only for Outgoing and Internal transfers
- Visible only when picking state is "Assigned"
- Reorders all move lines by:
  1. Location `pick_sequence` (ascending)
  2. Location `complete_name` (alphabetical fallback)

### 2. Pick Sequence Field
- Field: `pick_sequence` (Integer)
- Added to `stock.location` model
- Default value: 0
- Lower numbers are picked first
- Used for custom location ordering

### 3. Pick Sequence Management Menu
- Access via: **Inventory > Configuration > Pick Sequences**
- Tree view of all warehouse locations
- Editable directly in tree (inline editing)
- Filters for internal/customer/supplier locations
- Shows complete location hierarchy

### 4. Optimized Pick List Report
- Report name: "Optimized Pick List"
- Available on all stock.picking forms
- PDF output showing:
  - Picking reference and date
  - Operator assigned
  - Source and destination locations
  - Move lines in optimized order:
    - Product name
    - Product barcode (with Code128 visual barcode)
    - Lot/Serial number (if applicable)
    - Quantity and UoM
    - Source location (complete name)
    - Destination location (complete name)
  - Signature fields for operator and warehouse manager

## Usage Guide

### Setting Up Pick Sequences

1. Navigate to **Inventory > Configuration > Pick Sequences**
2. For each warehouse location, enter a `pick_sequence` number
3. Lower numbers = first to pick
4. Example layout for a 3-shelf warehouse:
   - Shelf A: pick_sequence = 10
   - Shelf B: pick_sequence = 20
   - Shelf C: pick_sequence = 30
5. Within each shelf, you can add sub-locations with intermediate sequences

### Optimizing a Pick

1. Open a transfer order (stock.picking) in state "Assigned"
2. Click **Optimize Pick Path** button
3. Move lines are automatically reordered by location sequence
4. Verify the order in the move lines grid
5. Click **Print Optimized Pick List** to generate PDF
6. Pickers use the optimized PDF for efficient route planning

### Using the Optimized Pick List PDF

1. After optimizing, click **Print Optimized Pick List**
2. PDF shows all items in shelf/location order
3. Pickers follow the numbered items in sequence
4. Reduces walking distance and time
5. PDF includes barcodes for barcode-scanner integration

## Technical Details

### Database Fields

**stock.location**
- `pick_sequence` (Integer): Custom picking sequence order

**stock.picking** (computed)
- `is_optimizable` (Boolean): True if outgoing or internal transfer

### Python Methods

**StockPicking.action_optimize_pick_path()**
- Reorders move_line_ids by location.pick_sequence and location.complete_name
- Updates line.sequence field to reflect new order
- Works with all move lines in the picking

**StockPicking._get_optimized_move_lines()**
- Returns move lines sorted by location sequence (used by report template)
- Does not modify data, read-only

**StockPicking.action_report_optimized_pick_list()**
- Triggers the QWeb PDF report generation
- Returns the report action

### Views and UI

- **stock_picking_views.xml**: Adds buttons to picking form
- **stock_location_views.xml**: Tree view for sequence editing, menu item
- **pick_list_report.xml**: QWeb PDF template

### Security

Module uses standard Odoo stock app security groups:
- `stock.group_stock_user`: Read access
- `stock.group_stock_manager`: Write access to sequences

## Configuration Best Practices

### For Small Warehouses (1-3 shelves)
```
Shelf A: 10
Shelf B: 20
Shelf C: 30
```

### For Medium Warehouses (multiple aisles)
```
Aisle 1, Shelf A: 100
Aisle 1, Shelf B: 110
Aisle 1, Shelf C: 120
Aisle 2, Shelf A: 200
Aisle 2, Shelf B: 210
Aisle 2, Shelf C: 220
```

### For Large Warehouses (zones + aisles + shelves)
```
Zone 1, Aisle A, Shelf 1: 1000
Zone 1, Aisle A, Shelf 2: 1010
Zone 1, Aisle B, Shelf 1: 1100
...
Zone 2, Aisle A, Shelf 1: 2000
```

## API Usage

### Optimize a picking programmatically:
```python
picking = self.env['stock.picking'].browse(picking_id)
picking.action_optimize_pick_path()
```

### Get optimized move lines:
```python
picking = self.env['stock.picking'].browse(picking_id)
optimized_lines = picking._get_optimized_move_lines()
```

### Generate optimized pick list PDF:
```python
picking = self.env['stock.picking'].browse(picking_id)
return picking.action_report_optimized_pick_list()
```

## Compatibility

- Odoo version: 18.0
- Depends on: `stock` module
- Python: 3.8+
- License: LGPL-3

## Support & Development

Module author: AMADIO
Website: https://amadio.io

## Version History

### v18.0.1.0.0 (Initial Release)
- Core pick path optimization
- Location sequence field
- Pick list PDF report
- Sequence management UI
- Full Odoo 18.0 support
