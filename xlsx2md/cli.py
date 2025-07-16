"""
CLI interface for xlsx2md.
"""

import sys
from pathlib import Path
from typing import List, Optional, Any
import logging

import typer
from rich.console import Console
from rich.table import Table

from .readers import read_file, get_reader
from .renderer import render_markdown_table
from .utils import get_output_stream
from .config import VERSION, ERROR_MESSAGES, SUPPORTED_FORMATS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xlsx2md.cli")

app = typer.Typer(
    name="xlsx2md",
    help="Convert Excel files (xlsx, xls) and CSV to Markdown tables",
    add_completion=False,
)


# Create console only when needed to avoid conflicts with tests
def get_console():
    """
    Get Rich console instance for colored output.

    Returns:
        Console: Rich console instance or None if not available
    """
    try:
        return Console()
    except Exception:
        # Fallback for test environment
        return None


def get_version() -> str:
    """
    Get formatted version string.

    Returns:
        str: Version string in format "xlsx2md {version}"
    """
    return f"xlsx2md {VERSION}"


def version_callback(value: bool):
    """
    Callback function for version option.

    Args:
        value: Boolean flag indicating if version was requested

    Raises:
        typer.Exit: Exits the application after printing version
    """
    if value:
        print(get_version())
        raise typer.Exit()


def print_error(message: str):
    """
    Print error message with red color if console supports it.

    Args:
        message: Error message to display
    """
    console = get_console()
    if console:
        console.print(f"[red]Error: {message}[/red]")
    else:
        print(f"Error: {message}", file=sys.stderr)


def print_warning(message: str):
    """
    Print warning message with yellow color if console supports it.

    Args:
        message: Warning message to display
    """
    console = get_console()
    if console:
        console.print(f"[yellow]{message}[/yellow]")
    else:
        print(f"Warning: {message}", file=sys.stderr)


@app.command()
def main(
    file_path: str = typer.Argument(..., help="Input file path (xlsx, xls, or csv)"),
    sheet: Optional[str] = typer.Option(
        None, "--sheet", "-s", help="Sheet name or index (default: first sheet)"
    ),
    range: Optional[str] = typer.Option(
        None, "--range", "-r", help="Cell range (e.g., A1:B10)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: stdout)"
    ),
    style: str = typer.Option(
        "default", "--style", help="Table style: default, minimal, or grid"
    ),
    align: Optional[List[str]] = typer.Option(
        None, "--align", help="Column alignment: left, center, or right"
    ),
    empty: str = typer.Option("", "--empty", help="Value for empty cells"),
    list_sheets: bool = typer.Option(
        False, "--list-sheets", help="List all sheets in Excel file"
    ),
    info: bool = typer.Option(False, "--info", help="Show file information"),
    all_sheets: bool = typer.Option(False, "--all-sheets", help="Process all sheets"),
    sheets: Optional[str] = typer.Option(
        None, "--sheets", help="Process specific sheets (1,3,5 or 'Sheet1,Sheet3')"
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
    ),
) -> None:
    """
    Convert Excel files (xlsx, xls) and CSV to Markdown tables.

    Examples:
        xlsx2md data.xlsx
        xlsx2md data.xlsx --sheet "Sheet2" --range "A1:C10"
        xlsx2md data.xlsx --style grid --align center --empty "-"
        xlsx2md data.xlsx --all-sheets --output tables.md
        xlsx2md data.xlsx --list-sheets
    """
    try:
        logger.info(f"Start processing: {file_path}")
        # Validate file
        if not Path(file_path).exists():
            print_error(ERROR_MESSAGES["file_not_found"].format(file_path=file_path))
            sys.exit(1)

        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            print_error(
                ERROR_MESSAGES["unsupported_format"].format(
                    format=file_ext, supported=", ".join(SUPPORTED_FORMATS)
                )
            )
            sys.exit(1)

        # Get reader
        reader = get_reader(file_path)
        logger.info(f"Reader selected: {type(reader).__name__}")

        # Handle list-sheets option
        if list_sheets:
            logger.info("Listing sheets...")
            if hasattr(reader, "get_sheet_names"):
                sheet_names = reader.get_sheet_names(file_path)
                if sheet_names:
                    console = get_console()
                    if console:
                        table = Table(title="Available Sheets")
                        table.add_column("Index", style="cyan")
                        table.add_column("Name", style="green")
                        for i, name in enumerate(sheet_names):
                            table.add_row(str(i), name)
                        console.print(table)
                    else:
                        print("Available Sheets:")
                        print("Index | Name")
                        print("------|------")
                        for i, name in enumerate(sheet_names):
                            print(f"{i:5} | {name}")
                else:
                    print_warning("No sheets found in file")
            else:
                print_warning("Sheet listing not supported for this file type")
            return

        # Handle info option
        if info:
            logger.info("Show file info...")
            show_file_info(file_path, reader)
            return

        # Process sheets
        if all_sheets:
            logger.info("Processing all sheets...")
            process_all_sheets(file_path, reader, range, output, style, align, empty)
        elif sheets:
            logger.info(f"Processing specific sheets: {sheets}")
            process_specific_sheets(
                file_path, reader, sheets, range, output, style, align, empty
            )
        else:
            logger.info(f"Processing single sheet: {sheet}")
            process_single_sheet(
                file_path, reader, sheet, range, output, style, align, empty
            )

    except Exception as e:
        logger.exception("CLI error")
        print_error(str(e))
        sys.exit(1)


def show_file_info(file_path: str, reader: Any) -> None:
    """
    Display detailed information about the input file.

    Shows file size, type, number of sheets, and sheet details including
    row and column counts for each sheet.

    Args:
        file_path: Path to the input file
        reader: File reader instance with sheet information methods
    """
    try:
        # Basic file info
        file_path_obj = Path(file_path)
        size_mb = file_path_obj.stat().st_size / (1024 * 1024)

        console = get_console()
        if console:
            info_table = Table(title="File Information")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="green")

            info_table.add_row("File", file_path)
            info_table.add_row("Type", file_path_obj.suffix.upper())
            info_table.add_row("Size", f"{size_mb:.2f} MB")

            # Sheet info if available
            if hasattr(reader, "get_sheet_names"):
                sheet_names = reader.get_sheet_names(file_path)
                if sheet_names:
                    info_table.add_row("Sheets", str(len(sheet_names)))
                    for i, name in enumerate(sheet_names):
                        sheet_info = reader.get_sheet_info(file_path, i)
                        if sheet_info:
                            info_table.add_row(
                                f"  Sheet {i}",
                                f"{name} ({sheet_info.get('nrows', '?')} rows, "
                                f"{sheet_info.get('ncols', '?')} cols)",
                            )

            console.print(info_table)
        else:
            print("File Information:")
            print(f"File: {file_path}")
            print(f"Type: {file_path_obj.suffix.upper()}")
            print(f"Size: {size_mb:.2f} MB")

            # Sheet info if available
            if hasattr(reader, "get_sheet_names"):
                sheet_names = reader.get_sheet_names(file_path)
                if sheet_names:
                    print(f"Sheets: {len(sheet_names)}")
                    for i, name in enumerate(sheet_names):
                        sheet_info = reader.get_sheet_info(file_path, i)
                        if sheet_info:
                            print(
                                f"  Sheet {i}: {name} "
                                f"({sheet_info.get('nrows', '?')} rows, "
                                f"{sheet_info.get('ncols', '?')} cols)"
                            )

    except Exception as e:
        print_error(f"Error getting file info: {str(e)}")


def process_single_sheet(
    file_path: str,
    reader: Any,
    sheet: Optional[str],
    range: Optional[str],
    output: Optional[Path],
    style: str,
    align: Optional[List[str]],
    empty: str,
) -> None:
    """Process a single sheet."""
    try:
        # Parse sheet parameter
        sheet_param = None
        if sheet:
            try:
                sheet_param = int(sheet)
            except ValueError:
                sheet_param = sheet

        # Read data
        data = read_file(file_path, sheet_param, range, max_rows=None)

        if not data:
            print_warning("No data found")
            return

        # Render markdown
        markdown = render_markdown_table(data, style, align, empty)

        # Output
        with get_output_stream(str(output) if output else None) as stream:
            stream.write(markdown)
            if not output:  # stdout
                stream.write("\n")

    except Exception as e:
        print_error(f"Error processing sheet: {str(e)}")
        raise


def process_all_sheets(
    file_path: str,
    reader: Any,
    range: Optional[str],
    output: Optional[Path],
    style: str,
    align: Optional[List[str]],
    empty: str,
) -> None:
    """Process all sheets in file."""
    try:
        if not hasattr(reader, "get_sheet_names"):
            print_warning("Multiple sheets not supported for this file type")
            return

        sheet_names = reader.get_sheet_names(file_path)
        if not sheet_names:
            print_warning("No sheets found")
            return

        with get_output_stream(str(output) if output else None) as stream:
            for i, sheet_name in enumerate(sheet_names):
                # Sheet header
                if i > 0:
                    stream.write("\n\n---\n\n")
                stream.write(f"# Sheet: {sheet_name}\n\n")

                # Process sheet
                try:
                    data = read_file(file_path, i, range, max_rows=None)
                    if data:
                        markdown = render_markdown_table(data, style, align, empty)
                        stream.write(markdown)
                    else:
                        stream.write("*No data in this sheet*\n")
                except Exception as e:
                    stream.write(f"*Error processing sheet: {str(e)}*\n")

                stream.write("\n")

    except Exception as e:
        print_error(f"Error processing all sheets: {str(e)}")
        raise


def process_specific_sheets(
    file_path: str,
    reader: Any,
    sheets: str,
    range: Optional[str],
    output: Optional[Path],
    style: str,
    align: Optional[List[str]],
    empty: str,
) -> None:
    """Process specific sheets."""
    try:
        if not hasattr(reader, "get_sheet_names"):
            print_warning("Multiple sheets not supported for this file type")
            return

        # Parse sheets parameter
        sheet_list = []
        for item in sheets.split(","):
            item = item.strip().strip("\"'")
            try:
                sheet_list.append(int(item))
            except ValueError:
                sheet_list.append(item)

        sheet_names = reader.get_sheet_names(file_path)

        with get_output_stream(str(output) if output else None) as stream:
            for i, sheet_param in enumerate(sheet_list):
                # Sheet header
                if i > 0:
                    stream.write("\n\n---\n\n")

                sheet_name = None
                if isinstance(sheet_param, int):
                    if 0 <= sheet_param < len(sheet_names):
                        sheet_name = sheet_names[sheet_param]
                    else:
                        stream.write(f"# Sheet {sheet_param} (not found)\n\n")
                        continue
                else:
                    sheet_name = sheet_param

                stream.write(f"# Sheet: {sheet_name}\n\n")

                # Process sheet
                try:
                    data = read_file(file_path, sheet_param, range, max_rows=None)
                    if data:
                        markdown = render_markdown_table(data, style, align, empty)
                        stream.write(markdown)
                    else:
                        stream.write("*No data in this sheet*\n")
                except Exception as e:
                    stream.write(f"*Error processing sheet: {str(e)}*\n")

                stream.write("\n")

    except Exception as e:
        print_error(f"Error processing specific sheets: {str(e)}")
        raise


if __name__ == "__main__":
    app()
