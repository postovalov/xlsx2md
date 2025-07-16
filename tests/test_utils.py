"""
Tests for utility functions.
"""

import pytest
import tempfile

from xlsx2md.utils import (
    get_file_extension,
    is_supported_format,
    get_file_size_mb,
    validate_file_path,
    parse_cell_range,
    column_to_index,
    index_to_column,
    normalize_sheet_name,
    clean_cell_value,
    truncate_text,
    calculate_column_widths,
    format_cell_content,
)


class TestFileUtils:
    """Tests for file utility functions."""

    def test_get_file_extension(self):
        """Test getting file extension."""
        assert get_file_extension("file.xlsx") == ".xlsx"
        assert get_file_extension("file.XLSX") == ".xlsx"
        assert get_file_extension("file.xls") == ".xls"
        assert get_file_extension("file.csv") == ".csv"
        assert get_file_extension("file") == ""
        assert get_file_extension("file.txt") == ".txt"

    def test_is_supported_format(self):
        """Test checking supported format."""
        assert is_supported_format("file.xlsx") is True
        assert is_supported_format("file.xls") is True
        assert is_supported_format("file.csv") is True
        assert is_supported_format("file.txt") is False
        assert is_supported_format("file") is False

    def test_get_file_size_mb(self):
        """Test getting file size."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()

            size = get_file_size_mb(temp_file.name)
            assert size > 0
            assert isinstance(size, float)

    def test_get_file_size_mb_nonexistent(self):
        """Test getting size of non-existent file."""
        size = get_file_size_mb("nonexistent_file.txt")
        assert size == 0.0

    def test_validate_file_path(self):
        """Test file path validation."""
        with tempfile.NamedTemporaryFile() as temp_file:
            assert validate_file_path(temp_file.name) is True

        assert validate_file_path("nonexistent_file.txt") is False


class TestCellRangeUtils:
    """Tests for cell range utility functions."""

    def test_parse_cell_range_valid(self):
        """Test parsing valid cell range."""
        result = parse_cell_range("A1:B10")
        assert result == ((0, 0), (9, 1))

        result = parse_cell_range("C5:D20")
        assert result == ((4, 2), (19, 3))

    def test_parse_cell_range_empty(self):
        """Test parsing empty range."""
        result = parse_cell_range("")
        assert result == ((0, 0), (0, 0))

        result = parse_cell_range(None)
        assert result == ((0, 0), (0, 0))

    def test_parse_cell_range_invalid(self):
        """Test parsing invalid range."""
        with pytest.raises(ValueError):
            parse_cell_range("invalid")

        with pytest.raises(ValueError):
            parse_cell_range("A1:B")

        with pytest.raises(ValueError):
            parse_cell_range("A:B10")

    def test_column_to_index(self):
        """Test converting column letter to index."""
        assert column_to_index("A") == 0
        assert column_to_index("B") == 1
        assert column_to_index("Z") == 25
        assert column_to_index("AA") == 26
        assert column_to_index("AB") == 27
        assert column_to_index("AZ") == 51

    def test_index_to_column(self):
        """Test converting column index to letter notation."""
        assert index_to_column(0) == "A"
        assert index_to_column(1) == "B"
        assert index_to_column(25) == "Z"
        assert index_to_column(26) == "AA"
        assert index_to_column(27) == "AB"
        assert index_to_column(51) == "AZ"


class TestDataUtils:
    """Tests for data utility functions."""

    def test_normalize_sheet_name(self):
        """Test sheet name normalization."""
        assert normalize_sheet_name("Sheet1") == "sheet1"
        assert normalize_sheet_name("  My Sheet  ") == "my sheet"
        assert normalize_sheet_name("") == ""

    def test_clean_cell_value(self):
        """Test cleaning cell value."""
        assert clean_cell_value(None) == ""
        assert clean_cell_value("  test  ") == "test"
        assert clean_cell_value("test\nvalue") == "test value"
        assert clean_cell_value("test   value") == "test value"
        assert clean_cell_value(123) == "123"
        assert clean_cell_value(0) == "0"

    def test_truncate_text(self):
        """Test text truncation."""
        assert truncate_text("test", 10) == "test"
        assert truncate_text("very long text", 10) == "very lo..."
        assert truncate_text("", 5) == ""
        assert truncate_text("abc", 3) == "..."

    def test_calculate_column_widths(self):
        """Test calculating column widths."""
        data = [
            ["short", "very long text", "medium"],
            ["longer text", "short", "very very long text"],
        ]

        widths = calculate_column_widths(data, min_width=3, max_width=20)
        assert len(widths) == 3
        assert widths[0] >= 10  # "longer text"
        assert widths[1] >= 13  # "very long text"
        assert widths[2] == 19  # "very very long text" (length 19)

    def test_calculate_column_widths_empty(self):
        """Test calculating column widths for empty data."""
        assert calculate_column_widths([]) == []
        assert calculate_column_widths([[]]) == []

    def test_format_cell_content(self):
        """Test formatting cell content."""
        # Test left alignment
        assert format_cell_content("test", 10, "left") == "test      "

        # Test right alignment
        assert format_cell_content("test", 10, "right") == "      test"

        # Test center alignment
        assert format_cell_content("test", 10, "center") == "   test   "

        # Test long text truncation
        assert format_cell_content("very long text", 10, "left") == "very lo..."

        # Test default (left)
        assert format_cell_content("test", 10) == "test      "
