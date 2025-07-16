# xlsx2md

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/xlsx2md.svg)](https://badge.fury.io/py/xlsx2md)
[![Tests](https://github.com/postovalov/xlsx2md/workflows/Tests/badge.svg)](https://github.com/postovalov/xlsx2md/actions)
[![Coverage](https://img.shields.io/badge/coverage-80%25+-green.svg)](https://codecov.io/gh/postovalov/xlsx2md)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://github.com/postovalov/xlsx2md)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

**xlsx2md** is a powerful CLI tool for converting Excel files (`.xlsx`, `.xls`) and CSV to Markdown tables with support for multiple sheets, cell ranges, and various table styles.

## ✨ Features

- 🔄 **Format support**: Excel (.xlsx, .xls) and CSV files
- 📊 **Multiple sheets**: process all or selected sheets
- 🎨 **Table styles**: default, minimal, grid
- 📏 **Alignment**: left, center, right for columns
- 🔍 **Cell ranges**: process specific areas
- 📋 **File info**: view structure and metadata
- 🎯 **Flexible options**: empty cells, encodings, delimiters

## 🚀 Installation

### Using pip
```bash
pip install xlsx2md
```

### Using pipx (recommended)
```bash
pipx install xlsx2md
```

### From source
```bash
git clone https://github.com/postovalov/xlsx2md.git
cd xlsx2md
pip install -e .
```

## 🎯 Quick Start

### Basic usage
```bash
# Convert Excel file to Markdown
xlsx2md data.xlsx

# Convert with specific sheet
xlsx2md data.xlsx --sheet "Sheet2"

# Convert cell range
xlsx2md data.xlsx --range "A1:C10"

# Save to file
xlsx2md data.xlsx --output table.md
```

### Table style examples
```bash
# Default style
xlsx2md data.xlsx

# Minimal style
xlsx2md data.xlsx --style minimal

# Grid style
xlsx2md data.xlsx --style grid
```

## 📁 Supported Formats

| Format        | Extension | Description                |
|---------------|-----------|----------------------------|
| Excel 2007+   | `.xlsx`   | Modern Excel format        |
| Excel 97-2003 | `.xls`    | Legacy Excel format        |
| CSV           | `.csv`    | Text format with delimiter |

## 📖 Usage

### Basic syntax
```bash
xlsx2md [OPTIONS] FILE_PATH
```

### Parameters

#### Main parameter
- `FILE_PATH` - path to input file (required)

#### Sheet options
- `--sheet, -s TEXT` - sheet name or index (default: first sheet)
- `--all-sheets` - process all sheets
- `--sheets TEXT` - process specific sheets (1,3,5 or "Sheet1,Sheet3")
- `--list-sheets` - show all sheets

#### Range options
- `--range, -r TEXT` - cell range (e.g., A1:B10)

#### Output options
- `--output, -o PATH` - output file path (default: stdout)
- `--style TEXT` - table style: default, minimal, grid (default: default)
- `--align TEXT` - column alignment: left, center, right
- `--empty TEXT` - value for empty cells (default: empty string)

#### Info options
- `--info` - show file information
- `--version, -V` - show version and exit
- `--help, -h` - show help

## 📊 Examples

### 1. Basic conversion
```bash
xlsx2md sales_data.xlsx
```

**Result:**
```markdown
|  Product |  Q1 |  Q2 |  Q3 |  Q4 |
|----------|-----|-----|-----|-----|
| Widget A | 100 | 120 | 110 | 130 |
| Widget B |  80 |  90 |  85 |  95 |
| Widget C | 150 | 160 | 155 | 165 |
```

### 2. Table styles

#### Default style
```bash
xlsx2md data.xlsx --style default
```

#### Minimal style
```bash
xlsx2md data.xlsx --style minimal
```

**Result:**
```markdown
Product  |  Q1 |  Q2 |  Q3 |  Q4
---------|-----|-----|-----|-----
Widget A | 100 | 120 | 110 | 130
Widget B |  80 |  90 |  85 |  95
```

#### Grid style
```bash
xlsx2md data.xlsx --style grid
```

**Result:**
```markdown
+----------+-----+-----+-----+-----+
| Product  | Q1  | Q2  | Q3  | Q4  |
+----------+-----+-----+-----+-----+
| Widget A | 100 | 120 | 110 | 130 |
| Widget B | 80  | 90  | 85  | 95  |
+----------+-----+-----+-----+-----+
```

### 3. Column alignment
```bash
xlsx2md data.xlsx --align center
```

### 4. Handling empty cells
```bash
xlsx2md data.xlsx --empty "-"
```

### 5. Working with ranges
```bash
xlsx2md data.xlsx --range "B2:D5"
```

### 6. All sheets
```bash
xlsx2md data.xlsx --all-sheets --output all_tables.md
```

### 7. Specific sheets
```bash
xlsx2md data.xlsx --sheets "1,3,5"
xlsx2md data.xlsx --sheets "Sheet1,Sheet3"
```

### 8. File info
```bash
xlsx2md data.xlsx --list-sheets
xlsx2md data.xlsx --info
```

## ⚙️ Configuration

### Environment variables

| Variable                | Description                        | Default     |
|-------------------------|------------------------------------|-------------|
| `XLSX2MD_ENCODING`      | Encoding for CSV files             | `utf-8`     |
| `XLSX2MD_MAX_FILE_SIZE` | Max file size (MB)                 | `100`       |
| `XLSX2MD_MAX_ROWS`      | Max number of rows                 | `10000`     |
| `XLSX2MD_OUTPUT_FORMAT` | Output format                      | `markdown`  |
| `XLSX2MD_COLORS`        | Enable colored output              | `true`      |
| `XLSX2MD_VERBOSE`       | Verbose output                     | `false`     |
| `XLSX2MD_LOG_LEVEL`     | Logging level                      | `WARNING`   |

### Example usage
```bash
export XLSX2MD_ENCODING=cp1251
export XLSX2MD_MAX_FILE_SIZE=200
xlsx2md large_file.xlsx
```

## 🛠️ Development

### Install for development
```bash
git clone https://github.com/postovalov/xlsx2md.git
cd xlsx2md
pip install -e ".[dev]"
```

### Run tests
```bash
# All tests
pytest

# With coverage
pytest --cov=xlsx2md

# Specific tests
pytest tests/test_cli.py
```

### Code quality
```bash
# Formatting
black xlsx2md tests

# Linting
flake8 xlsx2md tests

# Type checking
mypy xlsx2md
```

### Pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 📋 Requirements

- Python 3.8+
- openpyxl >= 3.0.0
- xlrd >= 2.0.0
- typer >= 0.9.0
- rich >= 13.0.0

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues

If you find a bug or have a suggestion, please create an issue on [GitHub](https://github.com/postovalov/xlsx2md/issues).

## 📈 Roadmap

- [ ] Google Sheets support
- [ ] Export to HTML tables
- [ ] Excel formulas support
- [ ] Interactive mode
- [ ] Plugin system for extensions

---

**Author**: Roman Postovalov
**Email**: rpostovalov@gmail.com
**GitHub**: [postovalov](https://github.com/postovalov)
