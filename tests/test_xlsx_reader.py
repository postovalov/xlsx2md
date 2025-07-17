"""
Tests for XLSX reader functionality.
"""

import pytest
from unittest.mock import Mock, patch
from xlsx2md.readers.xlsx_reader import XLSXReader


def test_corrupted_file_with_none_active_sheet(tmp_path):
    """Test handling of corrupted XLSX file where workbook.active returns None."""
    # Create a mock workbook with None active sheet but available worksheets
    mock_workbook = Mock()
    mock_workbook.active = None
    mock_workbook.sheetnames = ["Sheet1", "Sheet2"]

    mock_sheet1 = Mock()
    mock_sheet1.title = "Sheet1"
    mock_sheet1.max_row = 2
    mock_sheet1.max_column = 2
    mock_sheet1.cell.return_value.value = "test"

    mock_workbook.worksheets = [mock_sheet1, Mock()]

    reader = XLSXReader()

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        # Should use first available sheet when active is None
        data = reader.read(str(tmp_path / "test.xlsx"))

        # Verify that first sheet was used
        assert len(data) > 0
        mock_sheet1.cell.assert_called()


def test_corrupted_file_with_no_sheets(tmp_path):
    """Test handling of corrupted XLSX file with no sheets."""
    # Create a mock workbook with None active sheet and no worksheets
    mock_workbook = Mock()
    mock_workbook.active = None
    mock_workbook.sheetnames = []
    mock_workbook.worksheets = []

    reader = XLSXReader()

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        # Should raise ValueError when no sheets are available
        with pytest.raises(ValueError, match="no sheets found in workbook"):
            reader.read(str(tmp_path / "test.xlsx"))


def test_get_sheet_info_with_none_active_sheet(tmp_path):
    """Test get_sheet_info with corrupted file where workbook.active returns None."""
    # Create a mock workbook with None active sheet but available worksheets
    mock_workbook = Mock()
    mock_workbook.active = None
    mock_workbook.sheetnames = ["Sheet1"]

    mock_sheet = Mock()
    mock_sheet.title = "Sheet1"
    mock_sheet.max_row = 5
    mock_sheet.max_column = 3

    mock_workbook.worksheets = [mock_sheet]

    reader = XLSXReader()

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        # Should use first available sheet when active is None
        info = reader.get_sheet_info(str(tmp_path / "test.xlsx"))

        # Verify that info was retrieved from first sheet
        assert info["name"] == "Sheet1"
        assert info["max_row"] == 5
        assert info["max_column"] == 3


def test_get_sheet_info_with_no_sheets(tmp_path):
    """Test get_sheet_info with corrupted file with no sheets."""
    # Create a mock workbook with None active sheet and no worksheets
    mock_workbook = Mock()
    mock_workbook.active = None
    mock_workbook.sheetnames = []
    mock_workbook.worksheets = []

    reader = XLSXReader()

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        # Should return empty dict when no sheets are available
        info = reader.get_sheet_info(str(tmp_path / "test.xlsx"))
        assert info == {}


def test_normal_file_with_active_sheet(tmp_path):
    """Test normal file with valid active sheet."""
    # Create a mock workbook with valid active sheet
    mock_workbook = Mock()
    mock_sheet = Mock()
    mock_sheet.title = "ActiveSheet"
    mock_sheet.max_row = 3
    mock_sheet.max_column = 2
    mock_sheet.cell.return_value.value = "data"

    mock_workbook.active = mock_sheet
    mock_workbook.sheetnames = ["ActiveSheet"]
    mock_workbook.worksheets = [mock_sheet]

    reader = XLSXReader()

    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        # Should use active sheet normally
        data = reader.read(str(tmp_path / "test.xlsx"))

        # Verify that active sheet was used
        assert len(data) > 0
        mock_sheet.cell.assert_called()
