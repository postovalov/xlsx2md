"""
Markdown table renderer for xlsx2md.
"""

from typing import List, Optional, Literal
import logging

from .utils import calculate_column_widths, format_cell_content
from .config import ERROR_MESSAGES

logger = logging.getLogger(__name__)

TableStyle = Literal["default", "minimal", "grid"]
Alignment = Literal["left", "center", "right"]


def render_markdown_table(
    data: List[List[str]],
    style: TableStyle = "default",
    align: Optional[List[Alignment]] = None,
    empty_cell: str = "",
    min_width: int = 3,
    max_width: int = 50,
) -> str:
    """
    Render table data as Markdown formatted table.

    Converts 2D data array into Markdown table with specified style,
    alignment, and formatting options.

    Args:
        data: 2D list of strings representing table data (rows x columns)
        style: Table style - 'default' (standard markdown), 'minimal' (no borders),
               or 'grid' (ASCII box drawing)
        align: List of alignment options for each column ('left', 'center', 'right')
        empty_cell: String to use for empty/null cells
        min_width: Minimum column width in characters
        max_width: Maximum column width in characters

    Returns:
        str: Formatted Markdown table string

    Raises:
        ValueError: If style is not supported

    Examples:
        >>> data = [['Name', 'Age'], ['Alice', '25'], ['Bob', '30']]
        >>> render_markdown_table(data, style='default')
        '| Name  | Age |\\n|-------|-----|\\n| Alice | 25  |\\n| Bob   | 30  |'
    """
    if not data or not any(data):
        logger.warning("No data to render.")
        return ""

    # Replace empty cells
    table = [[cell if cell else empty_cell for cell in row] for row in data]

    # Calculate column widths
    col_widths = calculate_column_widths(table, min_width, max_width)
    num_cols = len(col_widths)

    # Alignment
    if align is None:
        align = ["left"] * num_cols
    else:
        align = (align + ["left"] * num_cols)[:num_cols]

    # Header and rows
    header = table[0]
    rows = table[1:]

    # Markdown alignment row
    align_map = {"left": ":---", "center": ":---:", "right": "---:"}
    align_row = [align_map.get(a, ":---") for a in align]

    # Render functions by style
    if style == "default":
        return _render_default(header, rows, col_widths, align_row, align, empty_cell)
    elif style == "minimal":
        return _render_minimal(header, rows, col_widths, align_row, align, empty_cell)
    elif style == "grid":
        return _render_grid(header, rows, col_widths, align_row, align, empty_cell)
    else:
        raise ValueError(ERROR_MESSAGES["invalid_style"].format(style=style))


def _render_default(header, rows, col_widths, align_row, align, empty_cell):
    """
    Render table in default Markdown style with pipe separators.

    Args:
        header: Header row data
        rows: Data rows
        col_widths: Calculated column widths
        align_row: Alignment row for markdown
        align: Column alignment options
        empty_cell: Value for empty cells

    Returns:
        str: Default style markdown table
    """
    # Header
    out = [
        "| "
        + " | ".join(
            format_cell_content(cell, w, a)
            for cell, w, a in zip(header, col_widths, align)
        )
        + " |"
    ]
    # Alignment
    out.append(
        "| "
        + " | ".join(
            format_cell_content(ar, w, a)
            for ar, w, a in zip(align_row, col_widths, align)
        )
        + " |"
    )
    # Rows
    for row in rows:
        out.append(
            "| "
            + " | ".join(
                format_cell_content(cell, w, a)
                for cell, w, a in zip(row, col_widths, align)
            )
            + " |"
        )
    return "\n".join(out)


def _render_minimal(header, rows, col_widths, align_row, align, empty_cell):
    """
    Render table in minimal style without borders.

    Args:
        header: Header row data
        rows: Data rows
        col_widths: Calculated column widths
        align_row: Alignment row (unused in minimal style)
        align: Column alignment options
        empty_cell: Value for empty cells

    Returns:
        str: Minimal style table without borders
    """
    # Header
    out = [
        " ".join(
            format_cell_content(cell, w, a)
            for cell, w, a in zip(header, col_widths, align)
        )
    ]
    # Alignment (skip)
    # Rows
    for row in rows:
        out.append(
            " ".join(
                format_cell_content(cell, w, a)
                for cell, w, a in zip(row, col_widths, align)
            )
        )
    return "\n".join(out)


def _render_grid(header, rows, col_widths, align_row, align, empty_cell):
    """
    Render table in grid style with ASCII box drawing characters.

    Args:
        header: Header row data
        rows: Data rows
        col_widths: Calculated column widths
        align_row: Alignment row (unused in grid style)
        align: Column alignment options
        empty_cell: Value for empty cells

    Returns:
        str: Grid style table with box borders
    """

    # Borders
    def border(char):
        return "+" + "+".join(char * (w + 2) for w in col_widths) + "+"

    # Header
    out = [border("-")]
    out.append(
        "|"
        + "|".join(
            " " + format_cell_content(cell, w, a) + " "
            for cell, w, a in zip(header, col_widths, align)
        )
        + "|"
    )
    out.append(border("="))
    # Rows
    for row in rows:
        out.append(
            "|"
            + "|".join(
                " " + format_cell_content(cell, w, a) + " "
                for cell, w, a in zip(row, col_widths, align)
            )
            + "|"
        )
        out.append(border("-"))
    return "\n".join(out)
