# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README.md with installation instructions and examples
- Complete docstrings for all public functions
- Usage examples in docs/examples/ directory
- Automatic example file generation script
- English localization for all documentation and code comments
- Badges for code quality, coverage, and build status
- Pre-commit hooks for code quality
- MyPy type checking configuration

### Changed
- Improved test coverage to 80%+
- Enhanced CLI error handling and validation
- Updated project structure and configuration

### Fixed
- Fixed failing tests in utils.py and validator.py
- Resolved flake8 issues and code formatting
- Fixed integration test data to use English

## [0.1.0] - 2024-01-XX

### Added
- Initial release of xlsx2md
- CLI interface using Typer
- Support for Excel files (.xlsx, .xls)
- Support for CSV files with various encodings
- Multiple table styles (default, minimal, grid)
- Column alignment options (left, center, right)
- Cell range selection (A1:B10 format)
- Multiple sheet processing
- Empty cell handling
- File information display
- Sheet listing functionality
- Comprehensive test suite
- Type hints throughout the codebase
- Configuration system with environment variables
- Error handling and validation
- Logging system for debugging

### Technical Details
- Python 3.8+ compatibility
- Dependencies: openpyxl, xlrd, typer, rich
- Development tools: pytest, black, flake8, mypy
- Pre-commit hooks for code quality
- PyPI-ready configuration

## [0.0.1] - 2024-01-XX

### Added
- Project structure and basic configuration
- Core modules: config, utils, validator
- File readers: xlsx, xls, csv
- Markdown renderer with multiple styles
- Basic CLI interface
- Initial test framework

---

## Version History

- **0.1.0**: First stable release with full CLI functionality
- **0.0.1**: Initial development version with core features

## Migration Guide

### From 0.0.1 to 0.1.0
- No breaking changes
- Enhanced CLI interface with additional options
- Improved error handling and validation
- Better test coverage and code quality

## Contributing

When adding new features or fixing bugs, please update this changelog following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### Changelog Entry Types
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Features that will be removed
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
