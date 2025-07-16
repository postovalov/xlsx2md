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
