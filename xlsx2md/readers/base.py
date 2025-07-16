"""
Base reader class for file reading operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
import logging

from ..utils import clean_cell_value, parse_cell_range
from ..config import MAX_ROWS_TO_READ

logger = logging.getLogger(__name__)


class BaseReader(ABC):
    """
    Abstract base class for all file readers.

    Provides common functionality for reading Excel and CSV files,
    including cell range filtering, row limiting, and data cleaning.
    All concrete reader implementations must inherit from this class.
    """

    def __init__(self):
        """
        Initialize base reader with default settings.

        Sets maximum rows to read from configuration.
        """
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
        """
        Read data from file.

        Abstract method that must be implemented by concrete reader classes.
        Each implementation should handle the specific file format and return
        data as a 2D list of strings.

        Args:
            file_path: Path to the file to read
            sheet_name_or_index: Sheet name or index (for Excel files only)
            cell_range: Cell range in A1:B10 format (e.g., "A1:C10")
            encoding: File encoding (for CSV files only)
            max_rows: Maximum number of rows to read (None for all rows)

        Returns:
            List[List[str]]: 2D list where each inner list represents a row

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If parameters are invalid or file is corrupted
        """
        pass

    def _apply_cell_range(
        self, data: List[List[str]], cell_range: str
    ) -> List[List[str]]:
        """
        Apply cell range filter to data.

        Args:
            data: Raw data
            cell_range: Cell range in A1:B10 format

        Returns:
            List[List[str]]: Filtered data
        """
        if not cell_range or not data:
            return data

        try:
            (start_row, start_col), (end_row, end_col) = parse_cell_range(cell_range)

            # Ensure we don't exceed data bounds
            max_rows = len(data)
            max_cols = max(len(row) for row in data) if data else 0

            end_row = min(end_row, max_rows - 1)
            end_col = min(end_col, max_cols - 1)

            # Extract range
            result = []
            for i in range(start_row, end_row + 1):
                if i < len(data):
                    row = data[i]
                    row_data = []
                    for j in range(start_col, end_col + 1):
                        if j < len(row):
                            row_data.append(row[j])
                        else:
                            row_data.append("")
                    result.append(row_data)

            return result

        except ValueError as e:
            logger.warning(f"Invalid cell range '{cell_range}': {e}")
            return data

    def _limit_rows(
        self, data: List[List[str]], max_rows: Optional[int] = None
    ) -> List[List[str]]:
        """
        Limit number of rows in data.

        Args:
            data: Raw data
            max_rows: Maximum number of rows

        Returns:
            List[List[str]]: Limited data
        """
        if max_rows is None:
            max_rows = self.max_rows

        if max_rows <= 0:
            return data

        return data[:max_rows]

    def _clean_data(self, data: List[List[str]]) -> List[List[str]]:
        """
        Clean and normalize data.

        Args:
            data: Raw data

        Returns:
            List[List[str]]: Cleaned data
        """
        if not data:
            return []

        cleaned_data = []
        for row in data:
            cleaned_row = [clean_cell_value(cell) for cell in row]
            cleaned_data.append(cleaned_row)

        return cleaned_data

    def _validate_data(self, data: List[List[str]]) -> None:
        """
        Validate data structure.

        Args:
            data: Data to validate

        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, list):
            raise ValueError("Data must be a list")

        for i, row in enumerate(data):
            if not isinstance(row, list):
                raise ValueError(f"Row {i} must be a list")

            for j, cell in enumerate(row):
                if not isinstance(cell, (str, int, float, type(None))):
                    raise ValueError(
                        f"Cell at row {i}, column {j} has invalid type: {type(cell)}"
                    )

    def _normalize_data(self, data: List[List[str]]) -> List[List[str]]:
        """
        Normalize data structure (ensure all rows have same number of columns).

        Args:
            data: Raw data

        Returns:
            List[List[str]]: Normalized data
        """
        if not data:
            return []

        # Find maximum number of columns
        max_cols = max(len(row) for row in data) if data else 0

        # Normalize all rows to have same number of columns
        normalized_data = []
        for row in data:
            normalized_row = row.copy()
            while len(normalized_row) < max_cols:
                normalized_row.append("")
            normalized_data.append(normalized_row)

        return normalized_data
