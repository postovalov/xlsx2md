"""
Validation functions for xlsx2md.
"""

import os
from typing import List, Optional, Union
import logging

from .config import (
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE_MB,
    MAX_ROWS_TO_READ,
    ALLOWED_SHEET_NAME_CHARS,
    MAX_SHEET_NAME_LENGTH,
    ERROR_MESSAGES,
)
from .utils import get_file_extension, get_file_size_mb, parse_cell_range

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception for validation errors."""

    pass


def validate_file_format(file_path: str) -> None:
    """Validates file format."""
    if not file_path:
        raise ValidationError(
            ERROR_MESSAGES["file_path_not_specified"].format(file_path=file_path)
        )

    extension = get_file_extension(file_path)
    if extension not in SUPPORTED_FORMATS:
        raise ValidationError(
            ERROR_MESSAGES["unsupported_format"].format(
                format=extension, supported=", ".join(SUPPORTED_FORMATS)
            )
        )


def validate_file_exists(file_path: str) -> None:
    """Validates file existence."""
    if not os.path.exists(file_path):
        raise ValidationError(
            ERROR_MESSAGES["file_not_found"].format(file_path=file_path)
        )


def validate_file_access(file_path: str) -> None:
    """Validates file accessibility for reading."""
    if not os.access(file_path, os.R_OK):
        raise ValidationError(
            ERROR_MESSAGES["permission_error"].format(file_path=file_path)
        )


def validate_file_size(file_path: str, max_size_mb: Optional[float] = None) -> None:
    """Validates file size."""
    if max_size_mb is None:
        max_size_mb = MAX_FILE_SIZE_MB

    file_size = get_file_size_mb(file_path)
    if file_size > max_size_mb:
        raise ValidationError(
            ERROR_MESSAGES["file_too_large"].format(
                size=f"{file_size:.1f}", max_size=max_size_mb
            )
        )


def validate_sheet_name(sheet_name: str) -> None:
    """Validates sheet name correctness."""
    if not sheet_name:
        return  # Empty name is allowed

    if len(sheet_name) > MAX_SHEET_NAME_LENGTH:
        raise ValidationError(
            f"Sheet name too long: {len(sheet_name)} characters. "
            f"Maximum: {MAX_SHEET_NAME_LENGTH}"
        )

    # Check characters
    invalid_chars = set(sheet_name) - ALLOWED_SHEET_NAME_CHARS
    if invalid_chars:
        raise ValidationError(
            f"Invalid characters in sheet name: {''.join(invalid_chars)}"
        )


def validate_sheet_index(sheet_index: int, max_sheets: int) -> None:
    """Validates sheet index correctness."""
    if not isinstance(sheet_index, int):
        raise ValidationError("Sheet index must be a number")

    if sheet_index < 0:
        raise ValidationError("Sheet index cannot be negative")

    if sheet_index >= max_sheets:
        raise ValidationError(
            f"Sheet index {sheet_index} out of range. Maximum: {max_sheets - 1}"
        )


def validate_cell_range(range_str: str) -> None:
    """Validates cell range correctness."""
    if not range_str:
        return  # Empty range is allowed

    try:
        parse_cell_range(range_str)
    except ValueError as e:
        raise ValidationError(str(e))


def validate_output_path(output_path: str) -> None:
    """Validates output file path correctness."""
    if not output_path:
        return  # Empty path is allowed (stdout)

    # Check if directory exists or can be created
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_path, exist_ok=True)
        except OSError:
            raise ValidationError(f"Cannot create directory: {output_dir}")

    # Check write permissions
    if os.path.exists(output_path) and not os.access(output_path, os.W_OK):
        raise ValidationError(f"No write permission for file: {output_path}")


def validate_data_not_empty(data: List[List[str]]) -> None:
    """Validates that data is not empty."""
    if not data:
        raise ValidationError(ERROR_MESSAGES["empty_file"])

    # Check if there's at least one row with data
    has_data = False
    for row in data:
        if any(cell.strip() for cell in row):
            has_data = True
            break

    if not has_data:
        raise ValidationError(ERROR_MESSAGES["empty_file"])


def validate_data_range(
    data: List[List[str]], start_row: int, end_row: int, start_col: int, end_col: int
) -> None:
    """Validates data range correctness."""
    if not data:
        return

    max_rows = len(data)
    max_cols = max(len(row) for row in data) if data else 0

    if start_row >= max_rows:
        raise ValidationError(f"Start row {start_row} out of data range")

    if end_row >= max_rows:
        raise ValidationError(f"End row {end_row} out of data range")

    if start_row > end_row:
        raise ValidationError("Start row is greater than end row")

    if start_col >= max_cols:
        raise ValidationError(f"Start column {start_col} out of data range")

    if end_col >= max_cols:
        raise ValidationError(f"End column {end_col} out of data range")

    if start_col > end_col:
        raise ValidationError("Start column is greater than end column")


def validate_encoding(encoding: str) -> None:
    """Validates encoding correctness."""
    if not encoding:
        return  # Empty encoding is allowed (will use default)

    # List of supported encodings
    supported_encodings = ["utf-8", "cp1251", "latin-1", "iso-8859-1", "ascii"]

    if encoding.lower() not in supported_encodings:
        raise ValidationError(f"Unsupported encoding: {encoding}")


def validate_csv_delimiter(delimiter: str) -> None:
    """Validates CSV delimiter correctness."""
    if not delimiter:
        raise ValidationError("CSV delimiter cannot be empty")

    if len(delimiter) > 1:
        raise ValidationError("CSV delimiter must be a single character")


def validate_max_rows(max_rows: int) -> None:
    """Validates maximum number of rows."""
    if not isinstance(max_rows, int):
        raise ValidationError("Maximum number of rows must be a number")

    if max_rows <= 0:
        raise ValidationError("Maximum rows must be positive")

    if max_rows > MAX_ROWS_TO_READ:
        raise ValidationError(
            f"Maximum number of rows exceeds limit: {MAX_ROWS_TO_READ}"
        )


def validate_all(
    file_path: str,
    sheet_name_or_index: Optional[Union[str, int]] = None,
    cell_range: Optional[str] = None,
    output_path: Optional[str] = None,
    encoding: Optional[str] = None,
    max_rows: Optional[int] = None,
) -> None:
    """
    Performs complete validation of all parameters.

    Args:
        file_path: File path
        sheet_name_or_index: Sheet name or index
        cell_range: Cell range
        output_path: Output file path
        encoding: Encoding
        max_rows: Maximum number of rows

    Raises:
        ValidationError: If validation fails
    """
    # File validation
    validate_file_exists(file_path)
    validate_file_access(file_path)
    validate_file_format(file_path)
    validate_file_size(file_path)

    # Parameter validation
    if sheet_name_or_index is not None:
        if isinstance(sheet_name_or_index, str):
            validate_sheet_name(sheet_name_or_index)
        elif isinstance(sheet_name_or_index, int):
            if sheet_name_or_index < 0:
                raise ValidationError("Sheet index cannot be negative")

    if cell_range:
        validate_cell_range(cell_range)

    if output_path:
        validate_output_path(output_path)

    if encoding:
        validate_encoding(encoding)

    if max_rows:
        validate_max_rows(max_rows)

    logger.info("All parameters validation passed successfully")
