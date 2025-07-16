# xlsx2md API Documentation

This document provides detailed API reference for the xlsx2md library.

## Table of Contents

- [Core Functions](#core-functions)
- [CLI Interface](#cli-interface)
- [File Readers](#file-readers)
- [Rendering System](#rendering-system)
- [Utilities](#utilities)
- [Configuration](#configuration)

## Core Functions

### `xlsx2md.readers.read_file()`

Read data from file using appropriate reader.

```python
def read_file(
    file_path: str,
    sheet_name_or_index: Optional[Union[str, int]] = None,
    cell_range: Optional[str] = None,
    encoding: Optional[str] = None,
    max_rows: Optional[int] = None,
) -> List[List[str]]
```

**Parameters:**
- `file_path` (str): Path to the file to read
- `sheet_name_or_index` (Optional[Union[str, int]]): Sheet name or index (for Excel files only)
- `cell_range` (Optional[str]): Cell range in A1:B10 format (e.g., "A1:C10")
- `encoding` (Optional[str]): File encoding (for CSV files only, e.g., "utf-8", "cp1251")
- `max_rows` (Optional[int]): Maximum number of rows to read (None for all rows)

**Returns:**
- `List[List[str]]`: 2D list where each inner list represents a row

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file format is not supported or parameters are invalid

**Examples:**
```python
from xlsx2md.readers import read_file

# Read Excel file
data = read_file("data.xlsx", sheet_name_or_index="Sheet1")

# Read CSV with encoding
data = read_file("data.csv", encoding="utf-8", max_rows=100)

# Read specific range
data = read_file("data.xlsx", cell_range="A1:C10")
```

### `xlsx2md.readers.get_reader()`

Factory function to get appropriate reader for file type.

```python
def get_reader(file_path: str) -> BaseReader
```

**Parameters:**
- `file_path` (str): Path to the file to read

**Returns:**
- `BaseReader`: Appropriate reader instance for the file type

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file format is not supported

## CLI Interface

### `xlsx2md.cli.main()`

Main CLI function for converting files to Markdown.

```python
def main(
    file_path: str,
    sheet: Optional[str] = None,
    range: Optional[str] = None,
    output: Optional[Path] = None,
    style: str = "default",
    align: Optional[List[str]] = None,
    empty: str = "",
    list_sheets: bool = False,
    info: bool = False,
    all_sheets: bool = False,
    sheets: Optional[str] = None,
    version: bool = False,
) -> None
```

**Parameters:**
- `file_path` (str): Input file path (required)
- `sheet` (Optional[str]): Sheet name or index
- `range` (Optional[str]): Cell range (e.g., A1:B10)
- `output` (Optional[Path]): Output file path
- `style` (str): Table style (default, minimal, grid)
- `align` (Optional[List[str]]): Column alignment (left, center, right)
- `empty` (str): Value for empty cells
- `list_sheets` (bool): List all sheets
- `info` (bool): Show file information
- `all_sheets` (bool): Process all sheets
- `sheets` (Optional[str]): Process specific sheets
- `version` (bool): Show version and exit

## File Readers

### BaseReader

Abstract base class for all file readers.

```python
class BaseReader(ABC):
    def __init__(self):
        self.max_rows = MAX_ROWS_TO_READ

    @abstractmethod
    def read(
        self,
        file_path: str,
        sheet_name_or_index: Optional[Union[str, int]] = None,
        cell_range: Optional[str] = None,
        encoding: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> List[List[str]]:
        """Read data from file."""
        pass
```

### XLSXReader

Reader for Excel 2007+ (.xlsx) files.

```python
class XLSXReader(BaseReader):
    def read(self, file_path: str, ...) -> List[List[str]]:
        """Read data from .xlsx file."""
```

### XLSReader

Reader for Excel 97-2003 (.xls) files.

```python
class XLSReader(BaseReader):
    def read(self, file_path: str, ...) -> List[List[str]]:
        """Read data from .xls file."""
```

### CSVReader

Reader for CSV files.

```python
class CSVReader(BaseReader):
    def read(self, file_path: str, ...) -> List[List[str]]:
        """Read data from .csv file."""
```

## Rendering System

### `xlsx2md.renderer.render_markdown_table()`

Render table data as Markdown formatted table.

```python
def render_markdown_table(
    data: List[List[str]],
    style: TableStyle = "default",
    align: Optional[List[Alignment]] = None,
    empty_cell: str = "",
    min_width: int = 3,
    max_width: int = 50,
) -> str
```

**Parameters:**
- `data` (List[List[str]]): 2D list of strings representing table data
- `style` (TableStyle): Table style - 'default', 'minimal', or 'grid'
- `align` (Optional[List[Alignment]]): List of alignment options for each column
- `empty_cell` (str): String to use for empty/null cells
- `min_width` (int): Minimum column width in characters
- `max_width` (int): Maximum column width in characters

**Returns:**
- `str`: Formatted Markdown table string

**Raises:**
- `ValueError`: If style is not supported

**Examples:**
```python
from xlsx2md.renderer import render_markdown_table

data = [['Name', 'Age'], ['Alice', '25'], ['Bob', '30']]

# Default style
result = render_markdown_table(data, style='default')

# Grid style with center alignment
result = render_markdown_table(data, style='grid', align=['center', 'center'])
```

## Utilities

### `xlsx2md.utils.parse_cell_range()`

Parse cell range in A1:B10 format.

```python
def parse_cell_range(range_str: str) -> Tuple[Tuple[int, int], Tuple[int, int]]
```

**Parameters:**
- `range_str` (str): Cell range string (e.g., "A1:B10")

**Returns:**
- `Tuple[Tuple[int, int], Tuple[int, int]]`: ((start_row, start_col), (end_row, end_col))

### `xlsx2md.utils.column_to_index()`

Convert Excel column letter to numeric index.

```python
def column_to_index(column_str: str) -> int
```

**Parameters:**
- `column_str` (str): Column letter(s) (e.g., 'A', 'AA', 'Z')

**Returns:**
- `int`: 0-based column index

### `xlsx2md.utils.index_to_column()`

Convert numeric column index to Excel column letter.

```python
def index_to_column(index: int) -> str
```

**Parameters:**
- `index` (int): 0-based column index

**Returns:**
- `str`: Column letter notation (e.g., 'A', 'AA', 'Z')

### `xlsx2md.utils.calculate_column_widths()`

Calculate optimal column widths based on content.

```python
def calculate_column_widths(
    data: List[List[str]],
    min_width: int = 3,
    max_width: int = 50
) -> List[int]
```

**Parameters:**
- `data` (List[List[str]]): Table data as list of rows
- `min_width` (int): Minimum column width
- `max_width` (int): Maximum column width

**Returns:**
- `List[int]`: List of calculated widths for each column

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `XLSX2MD_ENCODING` | Encoding for CSV files | `utf-8` |
| `XLSX2MD_MAX_FILE_SIZE` | Max file size (MB) | `100` |
| `XLSX2MD_MAX_ROWS` | Max number of rows | `10000` |
| `XLSX2MD_OUTPUT_FORMAT` | Output format | `markdown` |
| `XLSX2MD_COLORS` | Enable colored output | `true` |
| `XLSX2MD_VERBOSE` | Verbose output | `false` |
| `XLSX2MD_LOG_LEVEL` | Logging level | `WARNING` |

### `xlsx2md.config.get_config()`

Get full configuration with environment variables support.

```python
def get_config() -> Dict[str, Any]
```

**Returns:**
- `Dict[str, Any]`: Configuration dictionary

## Error Handling

### Common Exceptions

- `FileNotFoundError`: File doesn't exist
- `ValueError`: Invalid parameters or unsupported format
- `PermissionError`: No access to file
- `UnicodeDecodeError`: Encoding issues with CSV files

### Error Messages

Error messages are defined in `xlsx2md.config.ERROR_MESSAGES`:

```python
ERROR_MESSAGES = {
    "file_not_found": "File not found: {file_path}",
    "unsupported_format": "Unsupported file format: {format}. Supported formats: {supported}",
    "sheet_not_found": "Sheet not found: {sheet_name}",
    "invalid_range": "Invalid cell range: {range_str}",
    # ... more error messages
}
```

## Examples

### Basic Usage

```python
from xlsx2md.readers import read_file
from xlsx2md.renderer import render_markdown_table

# Read data
data = read_file("sales.xlsx", sheet_name_or_index="Q1")

# Render as markdown
markdown = render_markdown_table(data, style="grid", align=["left", "center", "right"])

# Save to file
with open("output.md", "w") as f:
    f.write(markdown)
```

### Custom Reader

```python
from xlsx2md.readers import BaseReader

class CustomReader(BaseReader):
    def read(self, file_path: str, **kwargs) -> List[List[str]]:
        # Custom implementation
        return [["Header1", "Header2"], ["Data1", "Data2"]]
```

### Error Handling

```python
from xlsx2md.readers import read_file

try:
    data = read_file("nonexistent.xlsx")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid file: {e}")
```

## Performance Considerations

- Large files (>10MB) may require significant memory
- Use `max_rows` parameter to limit data processing
- CSV files with different encodings may need explicit encoding specification
- Excel files with many sheets may take longer to process

## Best Practices

1. Always handle exceptions when reading files
2. Use appropriate encoding for CSV files
3. Validate cell ranges before processing
4. Consider memory usage for large files
5. Use type hints for better code documentation
6. Test with various file formats and encodings
