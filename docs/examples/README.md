# xlsx2md Usage Examples

This directory contains example files and commands to demonstrate the capabilities of xlsx2md.

## 📁 File Structure

### Excel files
- `sample_data.xlsx` - Basic example with multiple sheets
- `sales_report.xlsx` - Sales report with formatting
- `inventory.xlsx` - Inventory with empty cells

### CSV files
- `users.csv` - List of users
- `products.csv` - Product catalog
- `data_utf8.csv` - Data in UTF-8 encoding
- `data_cp1251.csv` - Data in CP1251 encoding

## 🚀 Example Commands

### Basic usage
```bash
# Convert Excel file
xlsx2md docs/examples/sample_data.xlsx

# Convert CSV file
xlsx2md docs/examples/users.csv
```

### Working with sheets
```bash
# List all sheets
xlsx2md docs/examples/sample_data.xlsx --list-sheets

# Convert specific sheet
xlsx2md docs/examples/sample_data.xlsx --sheet "Sheet2"

# Convert all sheets
xlsx2md docs/examples/sample_data.xlsx --all-sheets --output all_sheets.md
```

### Table styles
```bash
# Default style
xlsx2md docs/examples/sales_report.xlsx --style default

# Minimal style
xlsx2md docs/examples/sales_report.xlsx --style minimal

# Grid style
xlsx2md docs/examples/sales_report.xlsx --style grid
```

### Cell ranges
```bash
# Convert range
xlsx2md docs/examples/inventory.xlsx --range "A1:C10"

# Convert with alignment
xlsx2md docs/examples/inventory.xlsx --range "B2:D8" --align center
```

### Handling empty cells
```bash
# Replace empty cells with "-"
xlsx2md docs/examples/inventory.xlsx --empty "-"

# Replace with "N/A"
xlsx2md docs/examples/inventory.xlsx --empty "N/A"
```

### CSV encodings
```bash
# UTF-8 (default)
xlsx2md docs/examples/data_utf8.csv

# CP1251 (Windows-1251)
XLSX2MD_ENCODING=cp1251 xlsx2md docs/examples/data_cp1251.csv
```

### Save to file
```bash
# Save to specific file
xlsx2md docs/examples/sales_report.xlsx --output sales_table.md

# Save with custom name
xlsx2md docs/examples/inventory.xlsx --output "inventory_$(date +%Y%m%d).md"
```

### File info
```bash
# Show file info
xlsx2md docs/examples/sample_data.xlsx --info
```

## 📊 Expected Results

Each example demonstrates different conversion aspects:

1. **sample_data.xlsx** - Multiple sheets, various data types
2. **sales_report.xlsx** - Formatted numbers, dates, currencies
3. **inventory.xlsx** - Empty cells, long texts
4. **users.csv** - Simple data, standard structure
5. **products.csv** - Complex data, special characters

## 🔧 Testing

To test all examples, run:

```bash
# Generate all examples
make examples

# Test all commands
make test-examples
```

## 📝 Notes

- All example files are for demonstration purposes
- Real data may require additional configuration
- File encodings are indicated in filenames for clarity
- Results may vary depending on system and settings
