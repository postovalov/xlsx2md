# Release Checklist

## Pre-Release Preparation

### Code Quality
- [ ] All tests pass (`pytest`)
- [ ] Code coverage is acceptable (≥80%)
- [ ] Linting passes (`flake8`, `black`, `mypy`)
- [ ] Pre-commit hooks pass
- [ ] No TODO/FIXME comments in production code
- [ ] All functions have proper docstrings
- [ ] Type hints are complete and correct

### Documentation
- [ ] README.md is up to date
- [ ] API documentation is current
- [ ] CHANGELOG.md is updated with new changes
- [ ] Examples are working and up to date
- [ ] Installation instructions are correct
- [ ] All documentation is in English

### Testing
- [ ] Unit tests pass on all supported Python versions (3.8-3.13)
- [ ] Integration tests pass
- [ ] Manual testing with real files completed
- [ ] Test on different platforms (macOS, Linux, Windows)
- [ ] Test installation via pip and pipx
- [ ] Test CLI with various file formats and options

### Dependencies
- [ ] All dependencies are up to date
- [ ] No security vulnerabilities in dependencies
- [ ] `pyproject.toml` is properly configured
- [ ] `requirements.txt` is updated (if used)

## Release Process

### Version Management
- [ ] Update version in `xlsx2md/__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Create git tag for the version
- [ ] Update CHANGELOG.md with release date

### Build and Test
- [ ] Clean build directory
- [ ] Build package (`python -m build`)
- [ ] Test package installation
- [ ] Verify package contents
- [ ] Test CLI functionality after installation

### Publication
- [ ] Test upload to TestPyPI first
- [ ] Upload to PyPI
- [ ] Verify package is available on PyPI
- [ ] Test installation from PyPI
- [ ] Create GitHub release with release notes

### Post-Release
- [ ] Update documentation with new version
- [ ] Announce release (if applicable)
- [ ] Monitor for any issues
- [ ] Update development version number

## Emergency Procedures

### If Issues Found After Release
- [ ] Assess severity of the issue
- [ ] Create hotfix if necessary
- [ ] Follow same checklist for hotfix release
- [ ] Communicate with users if needed

### Rollback Plan
- [ ] Keep previous version available
- [ ] Document rollback procedure
- [ ] Have communication plan ready

## Quality Gates

### Must Pass (Blocking)
- [ ] All tests pass
- [ ] No critical security issues
- [ ] Basic functionality works
- [ ] Installation succeeds

### Should Pass (Warning)
- [ ] Code coverage ≥80%
- [ ] All linting rules pass
- [ ] Documentation is complete
- [ ] Examples work correctly

### Nice to Have
- [ ] Performance benchmarks pass
- [ ] All edge cases tested
- [ ] User feedback incorporated
- [ ] Release notes are comprehensive
