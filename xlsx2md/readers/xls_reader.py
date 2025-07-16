"""
XLS file reader implementation.
"""

from typing import List, Optional, Union
import logging

import xlrd

from .base import BaseReader

from ..config import ERROR_MESSAGES

logger = logging.getLogger(__name__)


class XLSReader(BaseReader):
    """Reader for XLS files."""

    def read(
        self,
        file_path: str,
        sheet_name_or_index: Optional[Union[str, int]] = None,
        cell_range: Optional[str] = None,
        encoding: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> List[List[str]]:
        """
        Read data from XLS file.

        Args:
            file_path: Path to the XLS file
            sheet_name_or_index: Sheet name or index (default: first sheet)
            cell_range: Cell range in A1:B10 format
            encoding: Not used for XLS files
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: Data as list of rows

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If sheet not found or invalid parameters
        """
        try:
            logger.info(f"Reading XLS file: {file_path}")

            # Open workbook
            workbook = xlrd.open_workbook(file_path)

            # Get sheet
            if sheet_name_or_index is None:
                sheet = workbook.sheet_by_index(0)
                logger.info(f"Using first sheet: {sheet.name}")
            else:
                sheet = self._get_sheet(workbook, sheet_name_or_index)
                logger.info(f"Using sheet: {sheet.name}")

            # Read data
            data = self._read_sheet_data(sheet, cell_range, max_rows)

            # Clean and normalize data
            data = self._clean_data(data)
            data = self._normalize_data(data)

            # Validate data
            self._validate_data(data)

            logger.info(f"Successfully read {len(data)} rows from XLS file")
            return data

        except FileNotFoundError:
            raise FileNotFoundError(
                ERROR_MESSAGES["file_not_found"].format(file_path=file_path)
            )
        except Exception as e:
            logger.error(f"Error reading XLS file {file_path}: {e}")
            raise ValueError(f"Failed to read XLS file: {e}")

    def _get_sheet(self, workbook, sheet_name_or_index: Union[str, int]):
        """
        Get sheet by name or index.

        Args:
            workbook: XLRD workbook object
            sheet_name_or_index: Sheet name or index

        Returns:
            XLRD sheet object

        Raises:
            ValueError: If sheet not found
        """
        if isinstance(sheet_name_or_index, int):
            if 0 <= sheet_name_or_index < workbook.nsheets:
                return workbook.sheet_by_index(sheet_name_or_index)
            else:
                raise ValueError(f"Sheet index {sheet_name_or_index} out of range")

        # Search by name
        try:
            return workbook.sheet_by_name(sheet_name_or_index)
        except xlrd.biffh.XLRDError:
            # Try case-insensitive search
            for i in range(workbook.nsheets):
                if workbook.sheet_name(i).lower() == sheet_name_or_index.lower():
                    return workbook.sheet_by_index(i)

            raise ValueError(
                ERROR_MESSAGES["sheet_not_found"].format(sheet_name=sheet_name_or_index)
            )

    def _read_sheet_data(
        self, sheet, cell_range: Optional[str] = None, max_rows: Optional[int] = None
    ) -> List[List[str]]:
        """
        Read data from worksheet.

        Args:
            sheet: XLRD sheet object
            cell_range: Cell range in A1:B10 format
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: Raw data from sheet
        """
        # Determine range to read
        if cell_range:
            data = self._read_cell_range(sheet, cell_range)
        else:
            data = self._read_all_data(sheet, max_rows)

        return data

    def _read_cell_range(self, sheet, cell_range: str) -> List[List[str]]:
        """
        Read data from specific cell range.

        Args:
            sheet: XLRD sheet object
            cell_range: Cell range in A1:B10 format

        Returns:
            List[List[str]]: Data from specified range
        """
        try:
            # Parse range
            from ..utils import parse_cell_range

            (start_row, start_col), (end_row, end_col) = parse_cell_range(cell_range)

            data = []
            for row_num in range(start_row, end_row + 1):
                if row_num < sheet.nrows:
                    row_data = []
                    for col_num in range(start_col, end_col + 1):
                        if col_num < sheet.ncols:
                            cell_value = sheet.cell_value(row_num, col_num)
                            row_data.append(cell_value)
                        else:
                            row_data.append("")
                    data.append(row_data)

            return data

        except Exception as e:
            logger.warning(f"Failed to read cell range {cell_range}: {e}")
            return self._read_all_data(sheet)

    def _read_all_data(self, sheet, max_rows: Optional[int] = None) -> List[List[str]]:
        """
        Read all data from worksheet.

        Args:
            sheet: XLRD sheet object
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: All data from sheet
        """
        data = []

        # Determine number of rows to read
        nrows = sheet.nrows
        if max_rows:
            nrows = min(nrows, max_rows)

        # Read data row by row
        for row_num in range(nrows):
            row_data = []
            for col_num in range(sheet.ncols):
                cell_value = sheet.cell_value(row_num, col_num)
                row_data.append(cell_value)

            # Skip empty rows
            if any(cell is not None and str(cell).strip() for cell in row_data):
                data.append(row_data)

        return data

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get list of sheet names in XLS file.

        Args:
            file_path: Path to the XLS file

        Returns:
            List[str]: List of sheet names
        """
        try:
            workbook = xlrd.open_workbook(file_path)
            return [workbook.sheet_name(i) for i in range(workbook.nsheets)]
        except Exception as e:
            logger.error(f"Error getting sheet names from {file_path}: {e}")
            return []

    def get_sheet_info(
        self, file_path: str, sheet_name_or_index: Optional[Union[str, int]] = None
    ) -> dict:
        """
        Get information about worksheet.

        Args:
            file_path: Path to the XLS file
            sheet_name_or_index: Sheet name or index

        Returns:
            dict: Sheet information
        """
        try:
            workbook = xlrd.open_workbook(file_path)

            if sheet_name_or_index is None:
                sheet = workbook.sheet_by_index(0)
            else:
                sheet = self._get_sheet(workbook, sheet_name_or_index)

            info = {
                "name": sheet.name,
                "nrows": sheet.nrows,
                "ncols": sheet.ncols,
                "dimensions": f"A1:{self._column_letter(sheet.ncols-1)}{sheet.nrows}",
            }

            return info

        except Exception as e:
            logger.error(f"Error getting sheet info from {file_path}: {e}")
            return {}

    def _column_letter(self, col_index: int) -> str:
        """
        Convert column index to letter notation.

        Args:
            col_index: Column index (0-based)

        Returns:
            str: Column letter (A, B, C, ...)
        """
        result = ""
        while col_index >= 0:
            col_index, remainder = divmod(col_index, 26)
            result = chr(ord("A") + remainder) + result
            col_index -= 1
        return result
