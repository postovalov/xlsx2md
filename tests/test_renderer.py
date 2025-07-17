"""
Tests for markdown table renderer.
"""

import pytest
from xlsx2md.renderer import render_markdown_table

BASIC_DATA = [["Name", "Age", "City"], ["Alice", "30", "New York"], ["Bob", "25", ""]]


def test_render_default():
    md = render_markdown_table(BASIC_DATA, style="default")
    assert "| Name" in md
    assert "| Age" in md
    assert "| City" in md
    assert md.count("|") > 5
    assert ":---" in md or "---:" in md


def test_render_minimal():
    md = render_markdown_table(BASIC_DATA, style="minimal")
    assert "|" not in md
    assert "Name" in md
    assert "Alice" in md
    assert "Bob" in md


def test_render_grid():
    md = render_markdown_table(BASIC_DATA, style="grid")
    assert md.startswith("+")
    assert "+" in md
    assert "| Name" in md or "|  Name" in md
    assert "New York" in md


def test_empty_cell():
    md = render_markdown_table(BASIC_DATA, style="default", empty_cell="-")
    assert "-" in md
    assert "| Bob" in md


def test_alignment_left():
    md = render_markdown_table(
        BASIC_DATA, style="default", align=["left", "left", "left"]
    )
    assert ":---" in md


def test_alignment_center():
    md = render_markdown_table(
        BASIC_DATA, style="default", align=["center", "center", "center"]
    )
    assert ":---:" in md


def test_alignment_right():
    md = render_markdown_table(
        BASIC_DATA, style="default", align=["right", "right", "right"]
    )
    assert "---:" in md


def test_invalid_style():
    with pytest.raises(ValueError):
        render_markdown_table(BASIC_DATA, style="unknown")


def test_empty_data():
    assert render_markdown_table([], style="default") == ""
    assert render_markdown_table([[]], style="default") == ""


# New tests for rendering quality


def test_column_alignment_consistency():
    """Checks that all lines have the same length and alignment."""
    data = [
        ["Name", "Age", "City"],
        ["Alice Johnson", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
        ["Charlie", "35", "Chicago"],
    ]

    md = render_markdown_table(data, style="default")
    lines = md.strip().split("\n")

    # Check that there are at least 3 lines (header, separator, data)
    assert len(lines) >= 3

    # Check that all lines have the same length
    line_lengths = [len(line) for line in lines]
    assert len(set(line_lengths)) == 1, f"Lines have different lengths: {line_lengths}"

    # Check that all lines start and end with |
    for line in lines:
        assert line.startswith("|"), f"Line does not start with |: {line}"
        assert line.endswith("|"), f"Line does not end with |: {line}"


def test_pipe_positions_consistency():
    """Checks that | separators are at the same positions in all lines."""
    data = [
        ["Product", "Price", "Stock"],
        ["Laptop", "$999", "15"],
        ["Mouse", "$25", "100"],
        ["Keyboard", "$75", "50"],
    ]

    md = render_markdown_table(data, style="default")
    lines = md.strip().split("\n")

    # Find positions of | in the first line (header)
    header_pipes = [i for i, char in enumerate(lines[0]) if char == "|"]

    # Check that in all lines | are at the same positions
    for line in lines:
        line_pipes = [i for i, char in enumerate(line) if char == "|"]
        assert (
            line_pipes == header_pipes
        ), f"Pipe positions do not match: {line_pipes} vs {header_pipes}"


def test_table_structure_integrity():
    """Checks table structural integrity."""
    data = [
        ["ID", "Name", "Email", "Status"],
        ["1", "John Doe", "john@example.com", "Active"],
        ["2", "Jane Smith", "jane@example.com", "Inactive"],
        ["3", "Bob Wilson", "bob@example.com", "Active"],
    ]

    md = render_markdown_table(data, style="default")
    lines = md.strip().split("\n")

    # Check number of lines (header + separator + data)
    expected_lines = len(data) + 1  # +1 for separator
    assert (
        len(lines) == expected_lines
    ), f"Expected {expected_lines} lines, got {len(lines)}"

    # Check that the separator line contains correct symbols
    separator_line = lines[1]
    assert "|" in separator_line
    assert (
        "---" in separator_line
        or ":---" in separator_line
        or "---:" in separator_line
        or ":---:" in separator_line
    )

    # Check number of columns in all lines
    for line in lines:
        pipe_count = line.count("|")
        assert (
            pipe_count == len(data[0]) + 1
        ), f"Incorrect number of columns in line: {line}"


def test_long_text_handling():
    """Checks handling and truncation of long text."""
    data = [
        ["Title", "Description", "Category"],
        ["Short", "This is a short description", "Test"],
        [
            "Long Title That Exceeds Normal Length",
            "Very long description that should be truncated when it exceeds "
            "the maximum width limit",
            "Long Category Name",
        ],
    ]

    md = render_markdown_table(data, style="default", max_width=20)
    lines = md.strip().split("\n")

    # Check that long text is truncated
    for line in lines:
        # Check that no cell exceeds the max width
        cells = line.split("|")[1:-1]  # Remove empty elements at start and end
        for cell in cells:
            cell_content = cell.strip()
            assert len(cell_content) <= 20, (
                f"Cell exceeds max width: '{cell_content}' "
                f"({len(cell_content)} chars)"
            )


def test_special_characters():
    """Checks correct rendering of special characters."""
    data = [
        ["Symbol", "Description", "Example"],
        ["pipe", "Pipe character", "Column separator"],
        ["*", "Asterisk", "**bold** text"],
        ["`", "Backtick", "`code` block"],
        ["[", "Bracket", "[link](url)"],
        ["(", "Parenthesis", "(text)"],
        ["#", "Hash", "# heading"],
        ["-", "Dash", "--- separator"],
    ]

    md = render_markdown_table(data, style="default")
    lines = md.strip().split("\n")

    # Check that special characters do not break table structure
    for line in lines:
        assert (
            line.count("|") == len(data[0]) + 1
        ), f"Special characters broke structure: {line}"

    # Check that special characters are present in output
    assert "*" in md
    assert "`" in md
    assert "[" in md
    assert "(" in md
    assert "#" in md
    assert "-" in md


def test_grid_style_borders():
    """Checks grid style borders correctness."""
    data = [
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
    ]

    md = render_markdown_table(data, style="grid")
    lines = md.strip().split("\n")

    # Check that table starts and ends with a border
    assert lines[0].startswith("+") and lines[0].endswith("+")
    assert lines[-1].startswith("+") and lines[-1].endswith("+")

    # Check that there is a separator line with =
    separator_found = False
    for line in lines:
        if "=" in line and line.startswith("+") and line.endswith("+"):
            separator_found = True
            break
    assert separator_found, "No separator line with = found in grid style"

    # Check that all data lines are surrounded by borders
    for i, line in enumerate(lines):
        if i > 0 and i < len(lines) - 1 and "=" not in line:
            # Data line should contain | and not be a border
            if not (line.startswith("+") and line.endswith("+")):
                assert "|" in line, f"Data line does not contain |: {line}"


def test_minimal_style_spacing():
    """Checks spacing correctness in minimal style."""
    data = [
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
    ]

    md = render_markdown_table(data, style="minimal")
    lines = md.strip().split("\n")

    # Check that there are no | symbols
    for line in lines:
        assert "|" not in line, f"Found | symbol in minimal style: {line}"

    # Check that there is a separator line with -
    separator_line = lines[1]
    assert "-" in separator_line, "No separator line found in minimal style"

    # Check that all lines have the same number of columns
    for line in lines:
        if line != separator_line:  # Skip separator line
            # Count columns by spaces (rough estimate)
            spaces = line.count(" ")
            assert spaces >= len(data[0]) - 1, f"Not enough columns in line: {line}"


def test_mixed_alignment():
    """Checks mixed column alignment."""
    data = [
        ["Name", "Age", "Salary", "Status"],
        ["Alice Johnson", "30", "$50000", "Active"],
        ["Bob Smith", "25", "$45000", "Inactive"],
        ["Charlie Brown", "35", "$60000", "Active"],
    ]

    # Mixed alignment: left, center, right, center
    align = ["left", "center", "right", "center"]
    md = render_markdown_table(data, style="default", align=align)
    lines = md.strip().split("\n")

    # Check that the separator line contains correct alignment markers
    separator_line = lines[1]
    assert ":---" in separator_line  # left
    assert ":---:" in separator_line  # center
    assert "---:" in separator_line  # right

    # Check structural integrity
    for line in lines:
        assert (
            line.count("|") == len(data[0]) + 1
        ), f"Incorrect number of columns: {line}"


def test_empty_cells_consistency():
    """Checks consistency of empty cell handling."""
    data = [
        ["Name", "Age", "Email", "Phone"],
        ["Alice", "", "alice@example.com", ""],
        ["", "30", "", "555-1234"],
        ["Bob", "25", "bob@example.com", "555-5678"],
    ]

    # Test with different values for empty cells
    for empty_value in ["", "-", "N/A", " "]:
        md = render_markdown_table(data, style="default", empty_cell=empty_value)
        lines = md.strip().split("\n")

        # Check that all lines have the same structure
        for line in lines:
            assert (
                line.count("|") == len(data[0]) + 1
            ), f"Incorrect structure with empty_cell='{empty_value}': {line}"

        # Check that empty cells are replaced with the specified value
        if empty_value:
            assert (
                empty_value in md
            ), f"Value empty_cell='{empty_value}' not found in output"


def test_default_style_complete_verification():
    """Complete verification of default style rendering."""
    data = [
        ["Product", "Price", "Stock", "Category"],
        ["Laptop", "$999", "15", "Electronics"],
        ["Mouse", "$25", "100", "Accessories"],
        ["Keyboard", "$75", "50", "Accessories"],
    ]

    md = render_markdown_table(data, style="default")
    lines = md.strip().split("\n")

    # Verify structure
    assert len(lines) == 5  # header + separator + 3 data rows

    # Verify header line
    header = lines[0]
    assert header.startswith("|") and header.endswith("|")
    assert "Product" in header
    assert "Price" in header
    assert "Stock" in header
    assert "Category" in header

    # Verify separator line
    separator = lines[1]
    assert separator.startswith("|") and separator.endswith("|")
    assert "---" in separator

    # Verify data lines
    for i in range(2, 5):
        data_line = lines[i]
        assert data_line.startswith("|") and data_line.endswith("|")
        assert data_line.count("|") == 5  # 4 columns + 2 borders

    # Verify content
    assert "Laptop" in md
    assert "$999" in md
    assert "15" in md
    assert "Electronics" in md


def test_minimal_style_complete_verification():
    """Complete verification of minimal style rendering."""
    data = [
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
        ["Charlie", "35", "Chicago"],
    ]

    md = render_markdown_table(data, style="minimal")
    lines = md.strip().split("\n")

    # Verify structure
    assert len(lines) == 5  # header + separator + 3 data rows

    # Verify no pipe symbols
    for line in lines:
        assert "|" not in line, f"Found pipe symbol in minimal style: {line}"

    # Verify header line
    header = lines[0]
    assert "Name" in header
    assert "Age" in header
    assert "City" in header

    # Verify separator line
    separator = lines[1]
    assert "-" in separator
    assert separator.count("-") >= 3  # At least 3 dashes

    # Verify data lines
    for i in range(2, 5):
        data_line = lines[i]
        assert "Alice" in data_line or "Bob" in data_line or "Charlie" in data_line

    # Verify content
    assert "Alice" in md
    assert "30" in md
    assert "New York" in md


def test_grid_style_complete_verification():
    """Complete verification of grid style rendering."""
    data = [
        ["ID", "Name", "Status"],
        ["1", "Alice", "Active"],
        ["2", "Bob", "Inactive"],
        ["3", "Charlie", "Active"],
    ]

    md = render_markdown_table(data, style="grid")
    lines = md.strip().split("\n")

    # Verify structure - grid style has borders between each row
    assert (
        len(lines) == 9
    )  # top border + header + separator + 3 data rows + 3 row borders

    # Verify top border
    top_border = lines[0]
    assert top_border.startswith("+") and top_border.endswith("+")
    assert top_border.count("+") >= 4  # At least 4 corners

    # Verify header line
    header = lines[1]
    assert header.startswith("|") and header.endswith("|")
    assert "ID" in header
    assert "Name" in header
    assert "Status" in header

    # Verify separator line
    separator = lines[2]
    assert separator.startswith("+") and separator.endswith("+")
    assert "=" in separator

    # Verify data lines with borders
    data_line_indices = [3, 5, 7]  # Data lines are at indices 3, 5, 7
    for i in data_line_indices:
        data_line = lines[i]
        assert data_line.startswith("|") and data_line.endswith("|")
        assert data_line.count("|") == 4  # 3 columns + 2 borders

    # Verify row borders
    border_indices = [0, 2, 4, 6, 8]  # Border lines
    for i in border_indices:
        border_line = lines[i]
        assert border_line.startswith("+") and border_line.endswith("+")
        assert border_line.count("+") >= 4

    # Verify content
    assert "1" in md
    assert "Alice" in md
    assert "Active" in md


def test_style_consistency_across_data_sizes():
    """Verify that all styles work consistently with different data sizes."""
    test_cases = [
        # Small table
        [["A", "B"], ["1", "2"]],
        # Medium table
        [["Name", "Age", "City"], ["Alice", "30", "NY"], ["Bob", "25", "LA"]],
        # Large table
        [
            ["ID", "Name", "Email", "Phone", "Status"],
            ["1", "Alice", "alice@test.com", "555-1234", "Active"],
            ["2", "Bob", "bob@test.com", "555-5678", "Inactive"],
            ["3", "Charlie", "charlie@test.com", "555-9012", "Active"],
            ["4", "Diana", "diana@test.com", "555-3456", "Active"],
        ],
    ]

    for data in test_cases:
        for style in ["default", "minimal", "grid"]:
            md = render_markdown_table(data, style=style)
            lines = md.strip().split("\n")

            # Verify basic structure
            assert len(lines) >= 3  # At least header + separator + 1 data row

            # Verify content is present
            for row in data:
                for cell in row:
                    if cell:  # Skip empty cells
                        assert cell in md, f"Cell '{cell}' not found in {style} style"

                        # Verify style-specific characteristics
                if style == "default":
                    assert "|" in lines[0]  # Header has pipes
                    # Separator might have different alignment markers
                    separator_line = lines[1]
                    assert (
                        "---" in separator_line
                        or ":---" in separator_line
                        or "---:" in separator_line
                        or ":---:" in separator_line
                        or "..." in separator_line
                    )
                elif style == "minimal":
                    assert "|" not in md  # No pipes anywhere
                    assert "-" in lines[1]  # Separator has dashes
                elif style == "grid":
                    assert lines[0].startswith("+") and lines[0].endswith(
                        "+"
                    )  # Top border
                    assert lines[-1].startswith("+") and lines[-1].endswith(
                        "+"
                    )  # Bottom border


def test_style_edge_cases():
    """Test edge cases for all table styles."""
    edge_cases = [
        # Single cell
        [["Single"]],
        # Single row
        [["A", "B", "C"]],
        # Single column
        [["Header"], ["Data1"], ["Data2"]],
        # Empty cells
        [["A", "", "C"], ["", "B", ""], ["D", "E", ""]],
        # Long content
        [["Short", "Very long content that might cause issues", "Normal"]],
        # Special characters
        [["Normal", "Text with | pipes", "Text with * asterisks"]],
    ]

    for data in edge_cases:
        for style in ["default", "minimal", "grid"]:
            try:
                md = render_markdown_table(data, style=style)
                lines = md.strip().split("\n")

                # Verify no crashes and basic structure
                assert len(lines) >= 2  # At least header + separator
                assert md != ""  # Not empty output

                # Verify style-specific requirements
                if style == "default":
                    assert "|" in lines[0]
                elif style == "minimal":
                    # Check that no line starts or ends with | (table structure)
                    for line in lines:
                        assert not line.strip().startswith(
                            "|"
                        ), f"Line starts with | in minimal style: {line}"
                        assert not line.strip().endswith(
                            "|"
                        ), f"Line ends with | in minimal style: {line}"
                elif style == "grid":
                    assert lines[0].startswith("+") and lines[0].endswith("+")

            except Exception as e:
                pytest.fail(f"Style {style} failed with data {data}: {e}")


def test_style_performance_with_large_data():
    """Test that all styles handle large datasets efficiently."""
    # Create large dataset
    large_data = [["ID", "Name", "Value", "Category"]]
    for i in range(100):  # 100 rows
        large_data.append([str(i), f"Item{i}", str(i * 10), f"Cat{i % 5}"])

    for style in ["default", "minimal", "grid"]:
        md = render_markdown_table(large_data, style=style)
        lines = md.strip().split("\n")

        # Verify all data is included
        if style == "grid":
            assert len(lines) == 203  # header + separator + 100 data rows + 101 borders
        else:
            assert len(lines) == 102  # header + separator + 100 data rows

        # Verify content is present
        assert "Item0" in md
        assert "Item99" in md
        assert "Cat0" in md
        assert "Cat4" in md

        # Verify style characteristics
        if style == "default":
            assert "|" in lines[0]
        elif style == "minimal":
            assert "|" not in md
        elif style == "grid":
            assert lines[0].startswith("+") and lines[0].endswith("+")
            assert lines[-1].startswith("+") and lines[-1].endswith("+")
