"""
Tests for file readers.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from xlsx2md.readers import (
    get_reader,
    read_file,
    BaseReader,
    XLSXReader,
    XLSReader,
    CSVReader,
)


class TestReaderFactory:
    """Tests for reader factory function."""

    def test_get_reader_xlsx(self):
        """Test getting XLSX reader."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            reader = get_reader(temp_file.name)
            assert isinstance(reader, XLSXReader)

    def test_get_reader_xls(self):
        """Test getting XLS reader."""
        with tempfile.NamedTemporaryFile(suffix=".xls") as temp_file:
            reader = get_reader(temp_file.name)
            assert isinstance(reader, XLSReader)

    def test_get_reader_csv(self):
        """Test getting CSV reader."""
        with tempfile.NamedTemporaryFile(suffix=".csv") as temp_file:
            reader = get_reader(temp_file.name)
            assert isinstance(reader, CSVReader)

    def test_get_reader_unsupported_format(self):
        """Test getting reader for unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            with pytest.raises(ValueError, match="Unsupported file format"):
                get_reader(temp_file.name)

    def test_get_reader_nonexistent_file(self):
        """Test getting reader for non-existent file."""
        with pytest.raises(FileNotFoundError):
            get_reader("nonexistent_file.xlsx")


class TestBaseReader:
    """Tests for base reader functionality."""

    class DummyReader(BaseReader):
        """Dummy reader for testing BaseReader methods."""

        def read(
            self,
            file_path: str,
            sheet_name_or_index=None,
            cell_range=None,
            encoding=None,
            max_rows=None,
        ):
            return []

    def test_apply_cell_range(self):
        """Test applying cell range filter."""
        reader = self.DummyReader()
        data = [["A1", "B1", "C1"], ["A2", "B2", "C2"], ["A3", "B3", "C3"]]

        # Test valid range
        result = reader._apply_cell_range(data, "A1:B2")
        expected = [["A1", "B1"], ["A2", "B2"]]
        assert result == expected

        # Test empty range
        result = reader._apply_cell_range(data, "")
        assert result == data

        # Test invalid range
        result = reader._apply_cell_range(data, "invalid")
        assert result == data

    def test_limit_rows(self):
        """Test limiting number of rows."""
        reader = self.DummyReader()
        data = [["A1"], ["A2"], ["A3"], ["A4"]]

        # Test with limit
        result = reader._limit_rows(data, 2)
        assert len(result) == 2
        assert result == [["A1"], ["A2"]]

        # Test without limit
        result = reader._limit_rows(data, None)
        assert result == data

        # Test with zero limit
        result = reader._limit_rows(data, 0)
        assert result == data

    def test_clean_data(self):
        """Test cleaning data."""
        reader = self.DummyReader()
        data = [["  A1  ", "B1\n", "C1   "], [None, "", "C2"]]

        result = reader._clean_data(data)
        expected = [["A1", "B1", "C1"], ["", "", "C2"]]
        assert result == expected

    def test_normalize_data(self):
        """Test normalizing data structure."""
        reader = self.DummyReader()
        data = [["A1", "B1"], ["A2"], ["A3", "B3", "C3"]]

        result = reader._normalize_data(data)
        expected = [["A1", "B1", ""], ["A2", "", ""], ["A3", "B3", "C3"]]
        assert result == expected

    def test_validate_data(self):
        """Test data validation."""
        reader = self.DummyReader()

        # Valid data
        valid_data = [["A1", "B1"], ["A2", "B2"]]
        reader._validate_data(valid_data)  # Should not raise

        # Invalid data - not a list
        with pytest.raises(ValueError, match="Data must be a list"):
            reader._validate_data("not a list")

        # Invalid data - row not a list
        with pytest.raises(ValueError, match="Row 0 must be a list"):
            reader._validate_data(["not a list"])

        # Invalid data - invalid cell type
        with pytest.raises(
            ValueError, match="Cell at row 0, column 0 has invalid type"
        ):
            reader._validate_data([[object()]])


class TestCSVReader:
    """Tests for CSV reader."""

    def test_read_csv_basic(self):
        """Test basic CSV reading."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                data = reader.read(temp_file.name)
                expected = [
                    ["Name", "Age", "City"],
                    ["Alice", "30", "New York"],
                    ["Bob", "25", "San Diego"],
                ]
                assert data == expected
            finally:
                os.unlink(temp_file.name)

    def test_read_csv_with_range(self):
        """Test CSV reading with cell range."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                data = reader.read(temp_file.name, cell_range="A1:B2")
                expected = [["Name", "Age"], ["Alice", "30"]]
                assert data == expected
            finally:
                os.unlink(temp_file.name)

    def test_read_csv_with_encoding(self):
        """Test CSV reading with specific encoding."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.close()

            try:
                data = reader.read(temp_file.name, encoding="utf-8")
                expected = [["Name", "Age"], ["Alice", "30"]]
                assert data == expected
            finally:
                os.unlink(temp_file.name)

    def test_read_csv_with_max_rows(self):
        """Test CSV reading with row limit."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.write("Bob,25\n")
            temp_file.write("Charlie,35\n")
            temp_file.close()

            try:
                data = reader.read(temp_file.name, max_rows=2)
                assert len(data) == 2
                assert data[0] == ["Name", "Age"]
                assert data[1] == ["Alice", "30"]
            finally:
                os.unlink(temp_file.name)

    def test_detect_delimiter(self):
        """Test delimiter detection."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name;Age;City\n")
            temp_file.write("Alice;30;New York\n")
            temp_file.close()

            try:
                delimiter = reader.detect_delimiter(temp_file.name)
                assert delimiter == ";"
            finally:
                os.unlink(temp_file.name)

    def test_get_file_info(self):
        """Test getting CSV file information."""
        reader = CSVReader()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.close()

            try:
                info = reader.get_file_info(temp_file.name)
                assert "encoding" in info
                assert "delimiter" in info
                assert "row_count" in info
                assert info["row_count"] == 2
            finally:
                os.unlink(temp_file.name)


class TestXLSXReader:
    """Tests for XLSX reader."""

    @patch("xlsx2md.readers.xlsx_reader.openpyxl.load_workbook")
    def test_read_xlsx_basic(self, mock_load_workbook):
        """Test basic XLSX reading."""
        reader = XLSXReader()

        # Mock workbook and sheet
        mock_sheet = MagicMock()
        mock_sheet.title = "Sheet1"
        mock_sheet.max_row = 3
        mock_sheet.max_column = 3

        # Create mock cell objects with proper value property
        def create_mock_cell(row, column):
            mock_cell = MagicMock()
            if row == 1 and column == 1:
                mock_cell.value = "Name"
            elif row == 1 and column == 2:
                mock_cell.value = "Age"
            elif row == 2 and column == 1:
                mock_cell.value = "Alice"
            elif row == 2 and column == 2:
                mock_cell.value = 30
            else:
                mock_cell.value = None
            return mock_cell

        mock_sheet.cell.side_effect = create_mock_cell

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet
        mock_workbook.sheetnames = ["Sheet1"]
        mock_load_workbook.return_value = mock_workbook

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            data = reader.read(temp_file.name)

            # Should have 2 rows (header + data)
            assert len(data) == 2
            assert data[0] == ["Name", "Age", ""]
            assert data[1] == ["Alice", "30", ""]

    @patch("xlsx2md.readers.xlsx_reader.openpyxl.load_workbook")
    def test_read_xlsx_with_sheet_name(self, mock_load_workbook):
        """Test XLSX reading with specific sheet name."""
        reader = XLSXReader()

        # Mock workbook and sheet
        mock_sheet = MagicMock()
        mock_sheet.title = "Sheet2"
        mock_sheet.max_row = 2
        mock_sheet.max_column = 2

        mock_sheet.cell.return_value.value = "Test"

        mock_workbook = MagicMock()
        mock_workbook.sheetnames = ["Sheet1", "Sheet2"]
        mock_workbook.worksheets = [MagicMock(), mock_sheet]
        mock_load_workbook.return_value = mock_workbook

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            data = reader.read(temp_file.name, sheet_name_or_index="Sheet2")
            assert len(data) > 0

    def test_get_sheet_names(self):
        """Test getting sheet names."""
        reader = XLSXReader()

        with patch("xlsx2md.readers.xlsx_reader.openpyxl.load_workbook") as mock_load:
            mock_workbook = MagicMock()
            mock_workbook.sheetnames = ["Sheet1", "Sheet2"]
            mock_load.return_value = mock_workbook

            with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
                names = reader.get_sheet_names(temp_file.name)
                assert names == ["Sheet1", "Sheet2"]


class TestXLSReader:
    """Tests for XLS reader."""

    @patch("xlsx2md.readers.xls_reader.xlrd.open_workbook")
    def test_read_xls_basic(self, mock_open_workbook):
        """Test basic XLS reading."""
        reader = XLSReader()

        # Mock workbook and sheet
        mock_sheet = MagicMock()
        mock_sheet.name = "Sheet1"
        mock_sheet.nrows = 2
        mock_sheet.ncols = 2

        def mock_cell_value(row, col):
            if row == 0 and col == 0:
                return "Name"
            elif row == 0 and col == 1:
                return "Age"
            elif row == 1 and col == 0:
                return "Alice"
            elif row == 1 and col == 1:
                return 30
            else:
                return ""

        mock_sheet.cell_value = mock_cell_value

        mock_workbook = MagicMock()
        mock_workbook.nsheets = 1
        mock_workbook.sheet_by_index.return_value = mock_sheet
        mock_workbook.sheet_name.return_value = "Sheet1"
        mock_open_workbook.return_value = mock_workbook

        with tempfile.NamedTemporaryFile(suffix=".xls") as temp_file:
            data = reader.read(temp_file.name)

            # Should have 2 rows (header + data)
            assert len(data) == 2
            assert data[0] == ["Name", "Age"]
            assert data[1] == ["Alice", "30"]

    def test_get_sheet_names(self):
        """Test getting sheet names."""
        reader = XLSReader()

        with patch("xlsx2md.readers.xls_reader.xlrd.open_workbook") as mock_open:
            mock_workbook = MagicMock()
            mock_workbook.nsheets = 2
            mock_workbook.sheet_name.side_effect = ["Sheet1", "Sheet2"]
            mock_open.return_value = mock_workbook

            with tempfile.NamedTemporaryFile(suffix=".xls") as temp_file:
                names = reader.get_sheet_names(temp_file.name)
                assert names == ["Sheet1", "Sheet2"]


class TestReadFileFunction:
    """Tests for read_file function."""

    def test_read_file_csv(self):
        """Test read_file function with CSV."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.close()

            try:
                data = read_file(temp_file.name)
                expected = [["Name", "Age"], ["Alice", "30"]]
                assert data == expected
            finally:
                os.unlink(temp_file.name)

    def test_read_file_with_parameters(self):
        """Test read_file function with parameters."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                data = read_file(temp_file.name, cell_range="A1:B2", max_rows=2)
                expected = [["Name", "Age"], ["Alice", "30"]]
                assert data == expected
            finally:
                os.unlink(temp_file.name)
