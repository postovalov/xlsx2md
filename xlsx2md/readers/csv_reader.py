"""
CSV file reader implementation.
"""

import csv
from typing import List, Optional, Union
import logging

from .base import BaseReader
from ..utils import detect_csv_encoding
from ..config import ERROR_MESSAGES, CSV_ENCODINGS

logger = logging.getLogger(__name__)


class CSVReader(BaseReader):
    """Reader for CSV files."""

    def read(
        self,
        file_path: str,
        sheet_name_or_index: Optional[Union[str, int]] = None,
        cell_range: Optional[str] = None,
        encoding: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> List[List[str]]:
        """
        Read data from CSV file.

        Args:
            file_path: Path to the CSV file
            sheet_name_or_index: Not used for CSV files
            cell_range: Cell range in A1:B10 format
            encoding: File encoding (auto-detected if not specified)
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: Data as list of rows

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If invalid parameters or encoding issues
        """
        try:
            logger.info(f"Reading CSV file: {file_path}")

            # Determine encoding
            if encoding is None:
                encoding = detect_csv_encoding(file_path)
                logger.info(f"Auto-detected encoding: {encoding}")
            else:
                logger.info(f"Using specified encoding: {encoding}")

            # Read data
            data = self._read_csv_data(file_path, encoding, max_rows)

            # Apply cell range if specified
            if cell_range:
                data = self._apply_cell_range(data, cell_range)

            # Clean and normalize data
            data = self._clean_data(data)
            data = self._normalize_data(data)

            # Validate data
            self._validate_data(data)

            logger.info(f"Successfully read {len(data)} rows from CSV file")
            return data

        except FileNotFoundError:
            raise FileNotFoundError(
                ERROR_MESSAGES["file_not_found"].format(file_path=file_path)
            )
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading CSV file {file_path}: {e}")
            raise ValueError(ERROR_MESSAGES["encoding_error"])
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise ValueError(f"Failed to read CSV file: {e}")

    def _read_csv_data(
        self, file_path: str, encoding: str, max_rows: Optional[int] = None
    ) -> List[List[str]]:
        """
        Read data from CSV file.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: Raw data from CSV file
        """
        data = []

        try:
            with open(file_path, "r", encoding=encoding, newline="") as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)

                # Use csv.Sniffer to detect dialect
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    logger.info(
                        f"Detected CSV dialect: delimiter='{dialect.delimiter}', "
                        f"quotechar='{dialect.quotechar}'"
                    )
                except csv.Error:
                    # Fallback to default dialect
                    dialect = csv.excel
                    logger.info("Using default CSV dialect")

                # Read CSV
                reader = csv.reader(csvfile, dialect=dialect)

                row_count = 0
                for row in reader:
                    if max_rows and row_count >= max_rows:
                        break

                    # Skip empty rows
                    if any(cell.strip() for cell in row):
                        data.append(row)

                    row_count += 1

        except UnicodeDecodeError:
            # Try alternative encodings
            for alt_encoding in CSV_ENCODINGS:
                if alt_encoding == encoding:
                    continue

                try:
                    logger.info(f"Trying alternative encoding: {alt_encoding}")
                    with open(
                        file_path, "r", encoding=alt_encoding, newline=""
                    ) as csvfile:
                        reader = csv.reader(csvfile)

                        row_count = 0
                        for row in reader:
                            if max_rows and row_count >= max_rows:
                                break

                            if any(cell.strip() for cell in row):
                                data.append(row)

                            row_count += 1

                    logger.info(f"Successfully read with encoding: {alt_encoding}")
                    break

                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Failed to read CSV file with any supported encoding")

        return data

    def read_with_delimiter(
        self,
        file_path: str,
        delimiter: str = ",",
        quotechar: str = '"',
        encoding: Optional[str] = None,
        max_rows: Optional[int] = None,
    ) -> List[List[str]]:
        """
        Read CSV file with specific delimiter and quote character.

        Args:
            file_path: Path to the CSV file
            delimiter: Field delimiter
            quotechar: Quote character
            encoding: File encoding
            max_rows: Maximum number of rows to read

        Returns:
            List[List[str]]: Data as list of rows
        """
        try:
            logger.info(
                f"Reading CSV file with delimiter '{delimiter}' and "
                f"quotechar '{quotechar}': {file_path}"
            )

            # Determine encoding
            if encoding is None:
                encoding = detect_csv_encoding(file_path)

            data = []

            with open(file_path, "r", encoding=encoding, newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)

                row_count = 0
                for row in reader:
                    if max_rows and row_count >= max_rows:
                        break

                    if any(cell.strip() for cell in row):
                        data.append(row)

                    row_count += 1

            # Clean and normalize data
            data = self._clean_data(data)
            data = self._normalize_data(data)

            logger.info(f"Successfully read {len(data)} rows from CSV file")
            return data

        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise ValueError(f"Failed to read CSV file: {e}")

    def detect_delimiter(self, file_path: str, encoding: Optional[str] = None) -> str:
        """
        Detect CSV delimiter.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding

        Returns:
            str: Detected delimiter
        """
        try:
            if encoding is None:
                encoding = detect_csv_encoding(file_path)

            with open(file_path, "r", encoding=encoding) as csvfile:
                sample = csvfile.read(1024)
                dialect = csv.Sniffer().sniff(sample)
                return dialect.delimiter

        except Exception as e:
            logger.warning(f"Failed to detect delimiter: {e}")
            return ","

    def get_file_info(self, file_path: str, encoding: Optional[str] = None) -> dict:
        """
        Get information about CSV file.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding

        Returns:
            dict: File information
        """
        try:
            if encoding is None:
                encoding = detect_csv_encoding(file_path)

            with open(file_path, "r", encoding=encoding) as csvfile:
                sample = csvfile.read(1024)
                csvfile.seek(0)

                # Count rows
                row_count = sum(1 for _ in csvfile)

                # Detect dialect
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                    quotechar = dialect.quotechar
                except csv.Error:
                    delimiter = ","
                    quotechar = '"'

            info = {
                "encoding": encoding,
                "delimiter": delimiter,
                "quotechar": quotechar,
                "row_count": row_count,
            }

            return info

        except Exception as e:
            logger.error(f"Error getting CSV file info from {file_path}: {e}")
            return {}
