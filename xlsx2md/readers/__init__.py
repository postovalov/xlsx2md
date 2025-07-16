"""
File readers package for xlsx2md.
"""

from typing import List, Optional, Union
import logging

from .base import BaseReader
from .xlsx_reader import XLSXReader
from .xls_reader import XLSReader
from .csv_reader import CSVReader

logger = logging.getLogger(__name__)


def get_reader(file_path: str) -> BaseReader:
    """
    Factory function to get appropriate reader for file type.

    Automatically selects the correct reader based on file extension:
    - .xlsx files -> XLSXReader
    - .xls files -> XLSReader
    - .csv files -> CSVReader

    Args:
        file_path: Path to the file to read

    Returns:
        BaseReader: Appropriate reader instance for the file type

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported

    Examples:
        >>> reader = get_reader("data.xlsx")
        >>> isinstance(reader, XLSXReader)
        True
    """
    import os

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    _, ext = os.path.splitext(file_path.lower())

    # Create appropriate reader
    if ext == ".xlsx":
        return XLSXReader()
    elif ext == ".xls":
        return XLSReader()
    elif ext == ".csv":
        return CSVReader()
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def read_file(
    file_path: str,
    sheet_name_or_index: Optional[Union[str, int]] = None,
    cell_range: Optional[str] = None,
    encoding: Optional[str] = None,
    max_rows: Optional[int] = None,
) -> List[List[str]]:
    """
    Read data from file using appropriate reader.

    High-level function that automatically selects the correct reader
    and returns the data as a 2D list of strings.

    Args:
        file_path: Path to the file to read
        sheet_name_or_index: Sheet name or index (for Excel files only)
        cell_range: Cell range in A1:B10 format (e.g., "A1:C10")
        encoding: File encoding (for CSV files only, e.g., "utf-8", "cp1251")
        max_rows: Maximum number of rows to read (None for all rows)

    Returns:
        List[List[str]]: 2D list where each inner list represents a row

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported or parameters are invalid

    Examples:
        >>> data = read_file("data.xlsx", sheet_name_or_index="Sheet1")
        >>> data = read_file("data.csv", encoding="utf-8", max_rows=100)
        >>> data = read_file("data.xlsx", cell_range="A1:C10")
    """
    reader = get_reader(file_path)
    return reader.read(file_path, sheet_name_or_index, cell_range, encoding, max_rows)


__all__ = [
    "BaseReader",
    "XLSXReader",
    "XLSReader",
    "CSVReader",
    "get_reader",
    "read_file",
]
