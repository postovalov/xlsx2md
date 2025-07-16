"""
Tests for validator module.
"""

import pytest

from xlsx2md.validator import (
    ValidationError,
    validate_file_format,
    validate_file_exists,
    validate_file_access,
    validate_file_size,
    validate_sheet_name,
    validate_sheet_index,
    validate_cell_range,
    validate_output_path,
    validate_data_not_empty,
    validate_data_range,
    validate_encoding,
    validate_csv_delimiter,
    validate_max_rows,
    validate_all,
)
from xlsx2md.config import (
    SUPPORTED_FORMATS,
    MAX_ROWS_TO_READ,
    MAX_SHEET_NAME_LENGTH,
)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test ValidationError can be created."""
        error = ValidationError("Test error")
        assert str(error) == "Test error"


class TestFileValidation:
    """Test file validation functions."""

    def test_validate_file_format_valid(self):
        """Test validate_file_format with valid formats."""
        for ext in SUPPORTED_FORMATS:
            validate_file_format(f"test{ext}")

    def test_validate_file_format_invalid(self):
        """Test validate_file_format with invalid format."""
        with pytest.raises(ValidationError, match="Unsupported file format"):
            validate_file_format("test.txt")

    def test_validate_file_format_empty_path(self):
        """Test validate_file_format with empty path."""
        with pytest.raises(ValidationError, match="File path not specified"):
            validate_file_format("")

    def test_validate_file_exists_valid(self, tmp_path):
        """Test validate_file_exists with existing file."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")
        validate_file_exists(str(test_file))

    def test_validate_file_exists_invalid(self):
        """Test validate_file_exists with non-existing file."""
        with pytest.raises(ValidationError, match="File not found"):
            validate_file_exists("nonexistent.xlsx")

    def test_validate_file_access_valid(self, tmp_path):
        """Test validate_file_access with accessible file."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")
        validate_file_access(str(test_file))

    def test_validate_file_size_valid(self, tmp_path):
        """Test validate_file_size with valid size."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")
        validate_file_size(str(test_file), max_size_mb=1.0)

    def test_validate_file_size_too_large(self, tmp_path):
        """Test validate_file_size with too large file."""
        test_file = tmp_path / "test.xlsx"
        # Create a file larger than 1MB
        test_file.write_text("x" * 1024 * 1024)
        with pytest.raises(ValidationError, match="File too large"):
            validate_file_size(str(test_file), max_size_mb=0.1)


class TestSheetValidation:
    """Test sheet validation functions."""

    def test_validate_sheet_name_valid(self):
        """Test validate_sheet_name with valid names."""
        valid_names = ["Sheet1", "My Sheet", "Sheet_123", ""]
        for name in valid_names:
            validate_sheet_name(name)

    def test_validate_sheet_name_too_long(self):
        """Test validate_sheet_name with too long name."""
        long_name = "x" * (MAX_SHEET_NAME_LENGTH + 1)
        with pytest.raises(ValidationError, match="Sheet name too long"):
            validate_sheet_name(long_name)

    def test_validate_sheet_name_invalid_chars(self):
        """Test validate_sheet_name with invalid characters."""
        invalid_names = ["Sheet[1]", "Sheet:2", "Sheet*3"]
        for name in invalid_names:
            with pytest.raises(ValidationError, match="Invalid characters"):
                validate_sheet_name(name)

    def test_validate_sheet_index_valid(self):
        """Test validate_sheet_index with valid indices."""
        validate_sheet_index(0, 5)
        validate_sheet_index(4, 5)

    def test_validate_sheet_index_invalid(self):
        """Test validate_sheet_index with invalid indices."""
        with pytest.raises(ValidationError, match="Sheet index must be a number"):
            validate_sheet_index("0", 5)

        with pytest.raises(ValidationError, match="Sheet index cannot be negative"):
            validate_sheet_index(-1, 5)

        with pytest.raises(ValidationError, match="Sheet index 5 out of range"):
            validate_sheet_index(5, 5)


class TestCellRangeValidation:
    """Test cell range validation functions."""

    def test_validate_cell_range_valid(self):
        """Test validate_cell_range with valid ranges."""
        valid_ranges = ["A1:B10", "A1", "B5:C20", ""]
        for range_str in valid_ranges:
            validate_cell_range(range_str)

    def test_validate_cell_range_invalid(self):
        """Test validate_cell_range with invalid ranges."""
        invalid_ranges = ["A1:B", "A:B10", "1:10", "A1:B-1"]
        for range_str in invalid_ranges:
            with pytest.raises(ValidationError):
                validate_cell_range(range_str)


class TestOutputPathValidation:
    """Test output path validation functions."""

    def test_validate_output_path_empty(self):
        """Test validate_output_path with empty path."""
        validate_output_path("")

    def test_validate_output_path_valid(self, tmp_path):
        """Test validate_output_path with valid path."""
        test_file = tmp_path / "output.md"
        validate_output_path(str(test_file))

    def test_validate_output_path_nonexistent_dir(self, tmp_path):
        """Test validate_output_path with nonexistent directory."""
        test_file = tmp_path / "nonexistent" / "output.md"
        # Should not raise error as directory can be created
        validate_output_path(str(test_file))


class TestDataValidation:
    """Test data validation functions."""

    def test_validate_data_not_empty_valid(self):
        """Test validate_data_not_empty with valid data."""
        valid_data = [["A", "B"], ["1", "2"]]
        validate_data_not_empty(valid_data)

    def test_validate_data_not_empty_invalid(self):
        """Test validate_data_not_empty with empty data."""
        with pytest.raises(ValidationError, match="File is empty"):
            validate_data_not_empty([])

        with pytest.raises(ValidationError, match="File is empty"):
            validate_data_not_empty([["", ""], ["", ""]])

    def test_validate_data_range_valid(self):
        """Test validate_data_range with valid range."""
        data = [["A", "B", "C"], ["1", "2", "3"], ["4", "5", "6"]]
        validate_data_range(data, 0, 2, 0, 2)

    def test_validate_data_range_invalid(self):
        """Test validate_data_range with invalid range."""
        data = [["A", "B"], ["1", "2"]]

        with pytest.raises(ValidationError, match="Start row 2 out of data range"):
            validate_data_range(data, 2, 3, 0, 1)

        with pytest.raises(ValidationError, match="Start row is greater than end row"):
            validate_data_range(data, 1, 0, 0, 1)


class TestEncodingValidation:
    """Test encoding validation functions."""

    def test_validate_encoding_valid(self):
        """Test validate_encoding with valid encodings."""
        valid_encodings = ["utf-8", "cp1251", "latin-1", "iso-8859-1", "ascii", ""]
        for encoding in valid_encodings:
            validate_encoding(encoding)

    def test_validate_encoding_invalid(self):
        """Test validate_encoding with invalid encoding."""
        with pytest.raises(ValidationError, match="Unsupported encoding"):
            validate_encoding("invalid-encoding")


class TestCSVDelimiterValidation:
    """Test CSV delimiter validation functions."""

    def test_validate_csv_delimiter_valid(self):
        """Test validate_csv_delimiter with valid delimiters."""
        valid_delimiters = [",", ";", "\t", "|"]
        for delimiter in valid_delimiters:
            validate_csv_delimiter(delimiter)

    def test_validate_csv_delimiter_invalid(self):
        """Test validate_csv_delimiter with invalid delimiters."""
        with pytest.raises(ValidationError, match="CSV delimiter cannot be empty"):
            validate_csv_delimiter("")

        with pytest.raises(
            ValidationError, match="CSV delimiter must be a single character"
        ):
            validate_csv_delimiter(",,")


class TestMaxRowsValidation:
    """Test max rows validation functions."""

    def test_validate_max_rows_valid(self):
        """Test validate_max_rows with valid values."""
        validate_max_rows(100)
        validate_max_rows(MAX_ROWS_TO_READ)

    def test_validate_max_rows_invalid(self):
        """Test validate_max_rows with invalid values."""
        with pytest.raises(ValidationError, match="Maximum rows must be positive"):
            validate_max_rows(0)

        with pytest.raises(ValidationError, match="Maximum rows must be positive"):
            validate_max_rows(-1)

        with pytest.raises(
            ValidationError, match="Maximum number of rows exceeds limit"
        ):
            validate_max_rows(MAX_ROWS_TO_READ + 1)


class TestValidateAll:
    """Test validate_all function."""

    def test_validate_all_valid(self, tmp_path):
        """Test validate_all with valid parameters."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")

        validate_all(
            file_path=str(test_file),
            sheet_name_or_index="Sheet1",
            cell_range="A1:B10",
            output_path="",
            encoding="utf-8",
            max_rows=100,
        )

    def test_validate_all_invalid_file(self):
        """Test validate_all with invalid file."""
        with pytest.raises(ValidationError, match="File not found"):
            validate_all(file_path="nonexistent.xlsx")
