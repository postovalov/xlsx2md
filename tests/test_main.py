"""
Tests for __main__.py module.
"""

from typer.testing import CliRunner

runner = CliRunner()


class TestMainModule:
    """Test __main__.py module."""

    def test_main_module_import(self):
        """Test that main module can be imported."""
        import xlsx2md.__main__

        assert hasattr(xlsx2md.__main__, "app")

    def test_main_module_structure(self):
        """Test that main module has correct structure."""
        import xlsx2md.__main__

        # Check that app is imported
        assert hasattr(xlsx2md.__main__, "app")

        # Check that app is callable
        assert callable(xlsx2md.__main__.app)

    def test_main_module_execution(self):
        """Test that main module can be executed."""
        # This test verifies that the module can be imported
        # without actually executing the CLI
        import xlsx2md.__main__

        assert xlsx2md.__main__ is not None

    def test_app_is_typer_instance(self):
        """Test that app is a Typer instance."""
        import xlsx2md.__main__
        import typer

        assert isinstance(xlsx2md.__main__.app, typer.Typer)
