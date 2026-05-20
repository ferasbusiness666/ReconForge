# ReconForge Improvements Roadmap

## Phase 1: Core Refactoring & Performance
- [x] Audit existing codebase
- [ ] Fix port scanning error handling (continue on error instead of breaking)
- [ ] Implement concurrent port scanning with ThreadPoolExecutor
- [ ] Add HTTP/HTTPS protocol detection in report generation
- [ ] Remove artificial 5-host limit in report generation
- [ ] Add timeout configuration options
- [ ] Improve banner grabbing robustness

## Phase 2: New Features
- [ ] Add JSON export format
- [ ] Add CSV export format
- [ ] Implement simple result caching (SQLite)
- [ ] Add filtering/sorting options for results
- [ ] Add rate limiting awareness
- [ ] Implement retry logic with exponential backoff
- [ ] Add custom port list support

## Phase 3: Testing & Quality
- [ ] Write unit tests for all modules
- [ ] Add integration tests
- [ ] Set up pytest configuration
- [ ] Add code coverage reporting
- [ ] Create GitHub Actions CI/CD pipeline
- [ ] Add pre-commit hooks (black, flake8, mypy)

## Phase 4: Packaging & Distribution
- [ ] Update version to 1.0.0
- [ ] Enhance setup.py with full metadata
- [ ] Create pyproject.toml for modern packaging
- [ ] Add project URLs (GitHub, docs, bug tracker)
- [ ] Create CONTRIBUTING.md
- [ ] Add CHANGELOG.md
- [ ] Prepare for PyPI publishing

## Phase 5: Documentation & Polish
- [ ] Rewrite README with better engagement
- [ ] Add installation troubleshooting section
- [ ] Create detailed usage guide
- [ ] Add examples for each command
- [ ] Create API documentation (if adding API mode)
- [ ] Add security best practices guide
- [ ] Create demo video/GIF

## Phase 6: Launch & Growth
- [ ] Push all changes to GitHub
- [ ] Create GitHub releases
- [ ] Submit to Awesome lists
- [ ] Post on Reddit/HackerNews
- [ ] Share on Twitter/X
- [ ] Add to security tool aggregators
