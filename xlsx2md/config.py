"""
Configuration settings for xlsx2md.
"""

import os
from typing import Dict, Any

# Default output formats
DEFAULT_TABLE_STYLE = {
    "border_chars": {
        "vertical": "|",
        "horizontal": "-",
        "corner": "+",
        "header_separator": "|",
    },
    "column_alignment": "left",
    "max_column_width": 50,
    "min_column_width": 3,
    "empty_cell_value": "",
    "header_separator": True,
}

# Supported file formats
SUPPORTED_FORMATS = [".xlsx", ".xls", ".csv"]
SUPPORTED_FORMATS_STR = ", ".join(SUPPORTED_FORMATS)

# File reading settings
DEFAULT_ENCODING = "utf-8"
CSV_ENCODINGS = ["utf-8", "cp1251", "latin-1", "iso-8859-1"]
MAX_FILE_SIZE_MB = 100
MAX_ROWS_TO_READ = 10000

# CLI settings
DEFAULT_OUTPUT_FORMAT = "markdown"
ENABLE_COLORS = True
VERBOSE_OUTPUT = False

# Validation settings
ALLOWED_SHEET_NAME_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "
)
MAX_SHEET_NAME_LENGTH = 31
DEFAULT_SHEET_INDEX = 0

# Constants
VERSION = "0.1.0"
AUTHOR = "Roman Postovalov"
EMAIL = "rpostovalov@gmail.com"
DESCRIPTION = "Convert Excel files (xlsx, xls) and CSV to Markdown tables"
PROJECT_URL = "https://github.com/postovalov/xlsx2md"

# Logging settings
LOG_LEVEL = os.getenv("XLSX2MD_LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance settings
CHUNK_SIZE = 1000  # Number of rows to process at once
MEMORY_LIMIT_MB = 512  # Memory limit for processing large files

# Output settings
OUTPUT_OPTIONS = {
    "markdown": {"extension": ".md", "mime_type": "text/markdown"},
    "text": {"extension": ".txt", "mime_type": "text/plain"},
}

# Error handling settings
ERROR_MESSAGES = {
    "file_not_found": "File not found: {file_path}",
    "unsupported_format": (
        "Unsupported file format: {format}. Supported formats: {supported}"
    ),
    "invalid_range": "Invalid cell range: {range_str}",
    "sheet_not_found": "Sheet not found: {sheet_name}",
    "invalid_encoding": "Unsupported encoding: {encoding}",
    "file_too_large": "File too large: {size}MB. Maximum size: {max_size}MB",
    "invalid_sheet_index": "Sheet index {sheet_index} out of range",
    "invalid_sheet_name": "Invalid characters in sheet name: {sheet_name}",
    "invalid_output_path": "Invalid output path: {output_path}",
    "file_path_not_specified": "File path not specified",
    "invalid_style": "Invalid table style: {style}",
    "empty_file": "File is empty or contains no data",
    "encoding_error": ("File encoding error. Try specifying encoding explicitly."),
    "permission_error": "No access to file: {file_path}",
    "no_data_in_range": "No data in specified range",
}

# Default settings for different file types
FILE_TYPE_DEFAULTS = {
    "xlsx": {"sheet_index": 0, "header_row": 0, "data_start_row": 1},
    "xls": {"sheet_index": 0, "header_row": 0, "data_start_row": 1},
    "csv": {
        "delimiter": ",",
        "quotechar": '"',
        "encoding": "utf-8",
        "header_row": 0,
        "data_start_row": 1,
    },
}


def get_config() -> Dict[str, Any]:
    """Returns full configuration with environment variables support."""
    config = {
        "table_style": DEFAULT_TABLE_STYLE.copy(),
        "supported_formats": SUPPORTED_FORMATS.copy(),
        "encoding": os.getenv("XLSX2MD_ENCODING", DEFAULT_ENCODING),
        "max_file_size_mb": int(os.getenv("XLSX2MD_MAX_FILE_SIZE", MAX_FILE_SIZE_MB)),
        "max_rows_to_read": int(os.getenv("XLSX2MD_MAX_ROWS", MAX_ROWS_TO_READ)),
        "output_format": os.getenv("XLSX2MD_OUTPUT_FORMAT", DEFAULT_OUTPUT_FORMAT),
        "enable_colors": os.getenv("XLSX2MD_COLORS", str(ENABLE_COLORS)).lower()
        == "true",
        "verbose": os.getenv("XLSX2MD_VERBOSE", str(VERBOSE_OUTPUT)).lower() == "true",
        "log_level": LOG_LEVEL,
        "chunk_size": int(os.getenv("XLSX2MD_CHUNK_SIZE", CHUNK_SIZE)),
        "memory_limit_mb": int(os.getenv("XLSX2MD_MEMORY_LIMIT", MEMORY_LIMIT_MB)),
    }
    return config
