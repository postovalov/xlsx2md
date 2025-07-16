"""
Utility functions for xlsx2md.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional, Union, Any
import logging
import contextlib

from .config import SUPPORTED_FORMATS, ERROR_MESSAGES

logger = logging.getLogger(__name__)


def get_file_extension(file_path: str) -> str:
    """
    Extract file extension from file path.

    Args:
        file_path: Path to the file

    Returns:
        str: File extension in lowercase (e.g., '.xlsx', '.csv')
    """
    return Path(file_path).suffix.lower()


def is_supported_format(file_path: str) -> bool:
    """
    Check if the file format is supported by xlsx2md.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if format is supported, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in SUPPORTED_FORMATS


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        float: File size in MB, 0.0 if error occurs
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError as e:
        logger.error(f"Error getting file size: {e}")
        return 0.0


def validate_file_path(file_path: str) -> bool:
    """
    Validate file existence, type, and read permissions.

    Args:
        file_path: Path to the file to validate

    Returns:
        bool: True if file is valid and accessible, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(ERROR_MESSAGES["file_not_found"].format(file_path=file_path))
        return False

    if not os.path.isfile(file_path):
        logger.error(f"Path is not a file: {file_path}")
        return False

    if not os.access(file_path, os.R_OK):
        logger.error(ERROR_MESSAGES["permission_error"].format(file_path=file_path))
        return False

    return True


def parse_cell_range(range_str: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Parses cell range in A1:B10 format or single cell A1 format.

    Returns:
        Tuple[Tuple[int, int], Tuple[int, int]]: ((start_row, start_col),
                                                   (end_row, end_col))
    """
    if not range_str:
        return (0, 0), (0, 0)

    # Remove spaces and convert to uppercase
    range_str = range_str.strip().upper()

    # Check A1:B10 format (range)
    range_pattern = r"^([A-Z]+)(\d+):([A-Z]+)(\d+)$"
    range_match = re.match(range_pattern, range_str)

    if range_match:
        start_col, start_row, end_col, end_row = range_match.groups()
        try:
            start_row = int(start_row) - 1  # Convert to 0-based index
            end_row = int(end_row) - 1
            start_col = column_to_index(start_col)
            end_col = column_to_index(end_col)
        except ValueError as e:
            raise ValueError(
                ERROR_MESSAGES["invalid_range"].format(range_str=range_str)
            ) from e
        return (start_row, start_col), (end_row, end_col)

    # Check A1 format (single cell)
    single_pattern = r"^([A-Z]+)(\d+)$"
    single_match = re.match(single_pattern, range_str)

    if single_match:
        col, row = single_match.groups()
        try:
            row = int(row) - 1  # Convert to 0-based index
            col = column_to_index(col)
        except ValueError as e:
            raise ValueError(
                ERROR_MESSAGES["invalid_range"].format(range_str=range_str)
            ) from e
        return (row, col), (row, col)

    raise ValueError(ERROR_MESSAGES["invalid_range"].format(range_str=range_str))


def column_to_index(column_str: str) -> int:
    """
    Convert Excel column letter notation to 0-based numeric index.

    Args:
        column_str: Column letter(s) (e.g., 'A', 'AA', 'Z')

    Returns:
        int: 0-based column index

    Examples:
        >>> column_to_index('A')
        0
        >>> column_to_index('AA')
        26
    """
    result = 0
    for char in column_str:
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1  # Convert to 0-based index


def index_to_column(index: int) -> str:
    """
    Convert 0-based numeric index to Excel column letter notation.

    Args:
        index: 0-based column index

    Returns:
        str: Column letter notation (e.g., 'A', 'AA', 'Z')

    Examples:
        >>> index_to_column(0)
        'A'
        >>> index_to_column(26)
        'AA'
    """
    result = ""
    while index >= 0:
        index, remainder = divmod(index, 26)
        result = chr(ord("A") + remainder) + result
        index -= 1
    return result


def normalize_sheet_name(sheet_name: str) -> str:
    """
    Normalize sheet name for case-insensitive search.

    Args:
        sheet_name: Original sheet name

    Returns:
        str: Normalized sheet name (lowercase, trimmed)
    """
    return sheet_name.strip().lower()


def find_sheet_by_name_or_index(
    workbook: Any, sheet_name_or_index: Union[str, int]
) -> Any:
    """
    Find worksheet by name or index in workbook.

    Args:
        workbook: Excel workbook object
        sheet_name_or_index: Sheet name (str) or index (int)

    Returns:
        Worksheet: Found worksheet object

    Raises:
        ValueError: If sheet is not found or index is out of range
    """
    if isinstance(sheet_name_or_index, int):
        if 0 <= sheet_name_or_index < len(workbook.sheetnames):
            return workbook.worksheets[sheet_name_or_index]
        else:
            raise ValueError(f"Sheet index {sheet_name_or_index} out of range")

    # Search by name
    normalized_name = normalize_sheet_name(sheet_name_or_index)

    for sheet in workbook.worksheets:
        if normalize_sheet_name(sheet.title) == normalized_name:
            return sheet

    # Try exact match
    for sheet in workbook.worksheets:
        if sheet.title == sheet_name_or_index:
            return sheet

    raise ValueError(
        ERROR_MESSAGES["sheet_not_found"].format(sheet_name=sheet_name_or_index)
    )


def clean_cell_value(value: Any) -> str:
    """
    Clean and normalize cell value for display.

    Removes extra whitespace, line breaks, and normalizes spacing.

    Args:
        value: Raw cell value from Excel/CSV

    Returns:
        str: Cleaned cell value, empty string if None
    """
    if value is None:
        return ""

    # Convert to string
    str_value = str(value).strip()

    # Remove extra spaces and line breaks
    str_value = re.sub(r"\s+", " ", str_value)

    return str_value


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to specified maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length

    Returns:
        str: Truncated text with "..." if needed

    Examples:
        >>> truncate_text("Hello World", 8)
        "Hello..."
        >>> truncate_text("Short", 10)
        "Short"
    """
    if max_length <= 3:
        return "..."

    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def calculate_column_widths(
    data: List[List[str]], min_width: int = 3, max_width: int = 50
) -> List[int]:
    """
    Calculate optimal column widths based on content.

    Analyzes all cells in each column to determine the minimum width
    needed to display the content without truncation, while respecting
    minimum and maximum width constraints.

    Args:
        data: Table data as list of rows
        min_width: Minimum column width
        max_width: Maximum column width

    Returns:
        List[int]: List of calculated widths for each column
    """
    if not data:
        return []

    num_columns = max(len(row) for row in data) if data else 0
    column_widths = [min_width] * num_columns

    for row in data:
        for i, cell in enumerate(row):
            if i < num_columns:
                cell_width = len(str(cell))
                # Cap width at max_width
                effective_width = min(cell_width, max_width)
                column_widths[i] = max(column_widths[i], effective_width, min_width)

    return column_widths


def format_cell_content(content: str, width: int, alignment: str = "left") -> str:
    """Formats cell content with width and alignment."""
    content = str(content)

    if len(content) > width:
        content = truncate_text(content, width)

    if alignment == "left":
        return content.ljust(width)
    elif alignment == "right":
        return content.rjust(width)
    elif alignment == "center":
        return content.center(width)
    else:
        return content.ljust(width)


def detect_csv_encoding(file_path: str) -> str:
    """Detects CSV file encoding."""
    import chardet

    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Read first 10KB to detect encoding
            result = chardet.detect(raw_data)
            return result["encoding"] or "utf-8"
    except Exception as e:
        logger.warning(f"Failed to detect encoding for file {file_path}: {e}")
        return "utf-8"


def ensure_output_directory(output_path: str) -> None:
    """Creates output directory if it doesn't exist."""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created directory: {output_dir}")


def get_output_stream(output_path: Optional[str] = None) -> Any:
    """Returns output stream (file or stdout)."""
    if output_path:
        logger.info(f"Writing output to file: {output_path}")
        ensure_output_directory(output_path)
        return open(output_path, "w", encoding="utf-8")
    else:
        logger.info("Writing output to stdout")
        import sys

        return contextlib.nullcontext(sys.stdout)
