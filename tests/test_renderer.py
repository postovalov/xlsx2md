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
