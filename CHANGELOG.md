# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-20

### Added
- **Concurrent port scanning** - Use ThreadPoolExecutor for faster multi-port scans
- **HTTP/HTTPS protocol detection** - Automatically try both protocols for technology detection
- **Comprehensive unit tests** - Full test coverage for all core modules
- **Development tooling** - pytest, black, flake8, mypy, pre-commit setup
- **CI/CD pipeline** - GitHub Actions workflow for automated testing
- **Enhanced packaging** - Better metadata, project URLs, and development dependencies
- **Contributing guide** - CONTRIBUTING.md with detailed guidelines
- **Changelog** - This file to track version history

### Changed
- **Port scanning** - Fixed error handling to continue scanning instead of breaking
- **Report generation** - Removed artificial 5-host limit, now scans all discovered subdomains
- **Version** - Bumped to 1.0.0 for production release
- **Dependencies** - Updated to latest stable versions of click, rich, requests

### Improved
- **Code quality** - Better error handling and edge case coverage
- **Performance** - Concurrent scanning significantly faster for large port lists
- **Documentation** - Enhanced README and new contributing guidelines
- **User experience** - Better error messages and progress feedback

### Fixed
- Port scanning now continues on DNS errors instead of stopping
- Technology detection now tries HTTP if HTTPS fails
- Improved banner grabbing timeout handling

## [0.1.0] - 2026-04-15

### Initial Release
- Subdomain discovery from certificate transparency data
- Common port scanning with banner grabbing
- HTTP technology detection
- Scope checking for targets
- Markdown report generation
- AI triage prompt library
- Rich terminal output with tables and spinners
