import subprocess
import sys


def run_cli(args, input_data=None):
    cmd = [sys.executable, "-m", "xlsx2md"] + args
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_csv_bom_to_markdown(tmp_path):
    """E2E: CSV with BOM -> Markdown"""
    content = "\ufeffName,Age\nIvan,22\nOlga,23\n"
    file = tmp_path / "bom.csv"
    file.write_text(content, encoding="utf-8-sig")
    result = run_cli([str(file)])
    assert result.returncode == 0
    assert "Ivan" in result.stdout
    assert "Olga" in result.stdout


def test_nonexistent_file():
    """E2E: Error for nonexistent file"""
    result = run_cli(["notfound.xlsx"])
    assert result.returncode != 0
    assert "not found" in result.stdout or "not found" in result.stderr
