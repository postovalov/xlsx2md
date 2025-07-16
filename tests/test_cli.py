"""
Tests for CLI interface.
"""

import tempfile
import os
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from xlsx2md.cli import app

runner = CliRunner()


class TestCLIBasic:
    """Basic CLI tests."""

    def test_help(self):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Convert Excel files" in result.stdout
        # Check for both --sheet and --sheets parameters (handle ANSI codes)
        help_output = (
            result.stdout.replace("\x1b[", "")
            .replace("\x1b[0m", "")
            .replace("\x1b[1m", "")
            .replace("\x1b[1;33m", "")
            .replace("\x1b[1;32m", "")
            .replace("\x1b[1;36m", "")
            .replace("\x1b[2m", "")
            .replace("\x1b[1;2;36m", "")
        )
        assert "--sheet" in help_output or "--sheets" in help_output
        assert "--output" in help_output

    def test_version(self):
        """Test version output."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "xlsx2md" in result.stdout

    def test_no_file(self):
        """Test error when no file provided."""
        result = runner.invoke(app, [])
        assert result.exit_code != 0

    def test_nonexistent_file(self):
        """Test error for non-existent file."""
        result = runner.invoke(app, ["nonexistent.xlsx"])
        assert result.exit_code != 0
        assert "File not found" in result.stdout

    def test_unsupported_format(self):
        """Test error for unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            result = runner.invoke(app, [temp_file.name])
            assert result.exit_code != 0
            assert "Unsupported file format" in result.stdout


class TestCLICSV:
    """CLI tests with CSV files."""

    def test_csv_basic(self):
        """Test basic CSV processing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                result = runner.invoke(app, [temp_file.name])
                assert result.exit_code == 0
                assert "| Name" in result.stdout
                assert "| Age" in result.stdout
                assert "| City" in result.stdout
                assert "Alice" in result.stdout
                assert "Bob" in result.stdout
            finally:
                os.unlink(temp_file.name)

    def test_csv_with_style(self):
        """Test CSV with different styles."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.close()

            try:
                # Test minimal style
                result = runner.invoke(app, [temp_file.name, "--style", "minimal"])
                assert result.exit_code == 0
                assert "|" not in result.stdout
                assert "Name" in result.stdout

                # Test grid style
                result = runner.invoke(app, [temp_file.name, "--style", "grid"])
                assert result.exit_code == 0
                assert "+" in result.stdout
            finally:
                os.unlink(temp_file.name)

    def test_csv_with_empty_cell(self):
        """Test CSV with empty cell value."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                result = runner.invoke(app, [temp_file.name, "--empty", "-"])
                assert result.exit_code == 0
                assert "-" in result.stdout
            finally:
                os.unlink(temp_file.name)

    def test_csv_with_range(self):
        """Test CSV with cell range."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                result = runner.invoke(app, [temp_file.name, "--range", "A1:B2"])
                assert result.exit_code == 0
                assert "Name" in result.stdout
                assert "Age" in result.stdout
                assert "City" not in result.stdout
            finally:
                os.unlink(temp_file.name)

    def test_csv_output_to_file(self):
        """Test CSV output to file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("Name,Age\n")
            input_file.write("Alice,30\n")
            input_file.close()

            with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as output_file:
                output_file.close()

                try:
                    result = runner.invoke(
                        app, [input_file.name, "--output", output_file.name]
                    )
                    assert result.exit_code == 0

                    # Check output file content
                    with open(output_file.name, "r") as f:
                        content = f.read()
                        assert "| Name" in content
                        assert "| Age" in content
                        assert "Alice" in content
                finally:
                    os.unlink(input_file.name)
                    os.unlink(output_file.name)


class TestCLIExcel:
    """CLI tests with Excel files (mocked)."""

    @patch("xlsx2md.cli.get_reader")
    @patch("xlsx2md.cli.read_file")
    def test_excel_basic(self, mock_read_file, mock_get_reader):
        """Test basic Excel processing."""
        # Mock data
        mock_data = [
            ["Name", "Age", "City"],
            ["Alice", "30", "New York"],
            ["Bob", "25", "San Diego"],
        ]
        mock_read_file.return_value = mock_data

        # Mock reader
        mock_reader = MagicMock()
        mock_get_reader.return_value = mock_reader

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            result = runner.invoke(app, [temp_file.name])
            assert result.exit_code == 0
            assert "| Name" in result.stdout
            assert "Alice" in result.stdout

    @patch("xlsx2md.cli.get_reader")
    def test_excel_list_sheets(self, mock_get_reader):
        """Test Excel list sheets functionality."""
        # Mock reader with sheet names
        mock_reader = MagicMock()
        mock_reader.get_sheet_names.return_value = ["Sheet1", "Sheet2", "Sheet3"]
        mock_get_reader.return_value = mock_reader

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            result = runner.invoke(app, [temp_file.name, "--list-sheets"])
            assert result.exit_code == 0
            assert "Sheet1" in result.stdout
            assert "Sheet2" in result.stdout
            assert "Sheet3" in result.stdout

    @patch("xlsx2md.cli.get_reader")
    def test_excel_info(self, mock_get_reader):
        """Test Excel info functionality."""
        # Mock reader with sheet info
        mock_reader = MagicMock()
        mock_reader.get_sheet_names.return_value = ["Sheet1", "Sheet2"]
        mock_reader.get_sheet_info.return_value = {
            "name": "Sheet1",
            "nrows": 10,
            "ncols": 5,
        }
        mock_get_reader.return_value = mock_reader

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            result = runner.invoke(app, [temp_file.name, "--info"])
            assert result.exit_code == 0
            assert "File Information" in result.stdout
            assert "Sheet1" in result.stdout


class TestCLIErrorHandling:
    """CLI error handling tests."""

    @patch("xlsx2md.cli.get_reader")
    def test_invalid_sheet(self, mock_get_reader):
        """Test error handling for invalid sheet."""
        # Mock reader that raises error for invalid sheet
        mock_reader = MagicMock()
        mock_get_reader.return_value = mock_reader

        with patch("xlsx2md.cli.read_file") as mock_read_file:
            mock_read_file.side_effect = ValueError("Sheet not found")

            with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
                result = runner.invoke(app, [temp_file.name, "--sheet", "InvalidSheet"])
                assert result.exit_code != 0
                assert "Error" in result.stdout

    @patch("xlsx2md.cli.get_reader")
    def test_invalid_range(self, mock_get_reader):
        """Test error handling for invalid range."""
        # Mock reader
        mock_reader = MagicMock()
        mock_get_reader.return_value = mock_reader

        with patch("xlsx2md.cli.read_file") as mock_read_file:
            mock_read_file.side_effect = ValueError("Invalid range")

            with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
                result = runner.invoke(app, [temp_file.name, "--range", "InvalidRange"])
                assert result.exit_code != 0
                assert "Error" in result.stdout

    def test_invalid_style(self):
        """Test error handling for invalid style."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age\n")
            temp_file.write("Alice,30\n")
            temp_file.close()

            try:
                result = runner.invoke(
                    app, [temp_file.name, "--style", "invalid_style"]
                )
                assert result.exit_code != 0
                assert "Error" in result.stdout
            finally:
                os.unlink(temp_file.name)


class TestCLIParameterCombinations:
    """CLI parameter combination tests."""

    def test_multiple_parameters(self):
        """Test multiple parameters together."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Name,Age,City\n")
            temp_file.write("Alice,30,New York\n")
            temp_file.write("Bob,25,San Diego\n")
            temp_file.close()

            try:
                result = runner.invoke(
                    app,
                    [
                        temp_file.name,
                        "--style",
                        "grid",
                        "--empty",
                        "-",
                        "--range",
                        "A1:B2",
                    ],
                )
                assert result.exit_code == 0
                assert "+" in result.stdout  # grid style
                assert "-" in result.stdout  # empty cell
                assert "Name" in result.stdout
                assert "Age" in result.stdout
            finally:
                os.unlink(temp_file.name)

    def test_output_with_style(self):
        """Test output file with style."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("Name,Age\n")
            input_file.write("Alice,30\n")
            input_file.close()

            with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as output_file:
                output_file.close()

                try:
                    result = runner.invoke(
                        app,
                        [
                            input_file.name,
                            "--output",
                            output_file.name,
                            "--style",
                            "minimal",
                        ],
                    )
                    assert result.exit_code == 0

                    # Check output file content
                    with open(output_file.name, "r") as f:
                        content = f.read()
                        assert "|" not in content  # minimal style
                        assert "Name" in content
                        assert "Alice" in content
                finally:
                    os.unlink(input_file.name)
                    os.unlink(output_file.name)
