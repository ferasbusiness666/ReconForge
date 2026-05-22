# Building ReconForge: Architecture & Design Decisions

**Published:** May 2026  
**Author:** Feras  
**Read Time:** 8 minutes

## Introduction

ReconForge started as a simple idea: automate the reconnaissance phase of security testing. What began as a basic CLI tool has evolved into a comprehensive, production-ready toolkit used by security researchers worldwide. In this post, I'll share the architectural decisions that make ReconForge fast, reliable, and easy to use.

## The Problem We Solved

Reconnaissance is the foundation of any security assessment. Yet it remains tedious and time-consuming:

- **Subdomain discovery** requires querying multiple sources and parsing results
- **Port scanning** can take hours when done sequentially
- **Technology detection** needs pattern matching across hundreds of signatures
- **Report generation** demands manual compilation of findings

Security researchers were spending 30-40% of their time on reconnaissance. ReconForge changes that.

## Architecture Overview

ReconForge follows a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│           CLI Interface                 │
│    (User-friendly command-line)         │
├─────────────────────────────────────────┤
│           Python API                    │
│    (Programmatic access layer)          │
├─────────────────────────────────────────┤
│         Core Modules                    │
│  ├─ Subdomains    ├─ PortScan          │
│  ├─ TechDetect    ├─ Analyzer          │
│  ├─ Cache         ├─ Export            │
│  └─ Config        └─ Logger            │
├─────────────────────────────────────────┤
│         External Services               │
│  ├─ crt.sh (Certificate logs)          │
│  ├─ HTTP Servers (Port scanning)       │
│  └─ Web Servers (Tech detection)       │
└─────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Modular Architecture

Each component has a single responsibility:

- **`subdomains.py`** - Certificate transparency queries only
- **`portscan.py`** - Port scanning and banner grabbing
- **`techdetect.py`** - Technology fingerprinting
- **`analyzer.py`** - Finding analysis and risk assessment
- **`export.py`** - Report generation in multiple formats
- **`cache.py`** - Result caching and persistence

**Benefits:**
- Easy to test each component independently
- Simple to add new features
- Reduced coupling between modules
- Clear separation of concerns

### 2. Concurrent Operations

Initial versions scanned ports sequentially. A domain with 50 subdomains could take 30+ minutes to scan.

**Solution:** ThreadPoolExecutor for concurrent scanning

```python
from concurrent.futures import ThreadPoolExecutor

def scan_ports(host, ports, concurrent=True):
    if concurrent:
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(scan_port, ports))
    else:
        results = [scan_port(p) for p in ports]
    return results
```

**Performance improvement:** 4x faster scans (30 minutes → 7 minutes)

**Trade-offs:**
- Slightly higher CPU usage
- Network rate limiting considerations
- Configurable worker count for tuning

### 3. Intelligent Caching

Recon results don't change frequently. Why re-query certificate logs every time?

**Caching strategy:**
- SQLite database for persistence
- Configurable TTL (default: 24 hours)
- Automatic cache invalidation
- Manual cache clearing option

```python
# First call: Queries crt.sh
result1 = api.discover_subdomains("example.com")

# Second call: Uses cache (instant)
result2 = api.discover_subdomains("example.com")

# Clear cache if needed
cache.clear()
```

**Benefits:**
- 100x faster repeated scans
- Reduced external API calls
- Offline capability for cached results
- Bandwidth savings

### 4. Error Resilience

Early versions failed completely if one port didn't respond. Production systems need better error handling.

**Implementation:**
- Try-catch blocks around each operation
- Graceful degradation (continue on errors)
- Detailed error logging
- User-friendly error messages

```python
def scan_ports(host, ports):
    results = []
    for port in ports:
        try:
            result = scan_port(host, port)
            results.append(result)
        except Exception as e:
            logger.warning(f"Failed to scan {host}:{port}: {e}")
            results.append({
                "port": port,
                "status": "error",
                "error": str(e)
            })
    return results
```

### 5. Configuration Management

Different users have different needs. Hard-coded values don't scale.

**Configuration system:**
- User-friendly CLI for settings
- Persistent storage in `~/.reconforge/config.json`
- Sensible defaults
- Environment variable overrides

```bash
# View configuration
reconforge config-show

# Update settings
reconforge config-set --key timeout --value 15.0
reconforge config-set --key max_workers --value 8

# Reset to defaults
reconforge config-reset
```

### 6. Multiple Export Formats

Different stakeholders need different formats:

- **Markdown** - For documentation and sharing
- **JSON** - For programmatic processing
- **HTML** - For web viewing
- **CSV** - For spreadsheet analysis

```bash
reconforge report -d example.com --format md   # Markdown
reconforge report -d example.com --format json # JSON
reconforge report -d example.com --format html # HTML
reconforge report -d example.com --format csv  # CSV
```

### 7. Dual Interface (CLI + API)

Not everyone wants to use the command line. Developers need programmatic access.

**CLI for:**
- Quick one-off scans
- Integration with shell scripts
- User-friendly output

**Python API for:**
- Programmatic access
- Integration with other tools
- Custom workflows
- Automation

```python
# CLI
$ reconforge subdomains -d example.com

# Python API
from reconforge.api import ReconForgeAPI
api = ReconForgeAPI()
result = api.discover_subdomains("example.com")
```

## Performance Optimizations

### Optimization 1: Connection Pooling

Multiple HTTP requests to the same server benefit from connection reuse.

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### Optimization 2: Lazy Loading

Don't load everything into memory at once.

```python
# Bad: Load all results at once
results = fetch_all_subdomains()

# Good: Stream results
for subdomain in fetch_subdomains_stream():
    process(subdomain)
```

### Optimization 3: Early Exit

Stop processing when we have enough information.

```python
# Stop after finding first vulnerability
for port in ports:
    if is_vulnerable(port):
        return port
```

## Testing Strategy

Comprehensive testing ensures reliability:

- **Unit tests** - Test individual functions (20+ tests)
- **Integration tests** - Test module interactions
- **Performance tests** - Ensure speed targets
- **Security tests** - Validate security practices

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=reconforge

# Run specific test
pytest tests/test_portscan.py::test_concurrent_scanning
```

## Lessons Learned

### Lesson 1: Start Simple

The first version was 200 lines of code. Adding features incrementally made it maintainable.

### Lesson 2: Listen to Users

Early adopters requested batch processing, caching, and export formats. These became core features.

### Lesson 3: Document Everything

Good documentation reduced support questions by 80%.

### Lesson 4: Embrace Concurrency

Concurrent operations were the biggest performance win. Worth the added complexity.

### Lesson 5: Make it Extensible

The API design allows users to build on ReconForge. This created a virtuous cycle of contributions.

## Future Architecture

The roadmap includes:

- **Async/await** - Replace ThreadPoolExecutor for better scalability
- **Database backend** - Store results in PostgreSQL for multi-user scenarios
- **Web dashboard** - Visual interface for report viewing
- **Machine learning** - AI-powered vulnerability detection
- **Distributed scanning** - Distribute scans across multiple machines

## Conclusion

ReconForge's architecture prioritizes:

1. **Modularity** - Easy to understand and extend
2. **Performance** - Fast enough for real-world use
3. **Reliability** - Handles errors gracefully
4. **Usability** - Both CLI and API interfaces
5. **Extensibility** - Built for community contributions

The result is a tool that's both powerful and accessible, used by security researchers worldwide.

## What's Next?

- Try ReconForge: `pip install reconforge`
- Read the docs: [github.com/ferasbusiness666/ReconForge](https://github.com/ferasbusiness666/ReconForge)
- Contribute: Check out [CONTRIBUTING.md](https://github.com/ferasbusiness666/ReconForge/blob/main/CONTRIBUTING.md)

---

**Questions or feedback?** Open a GitHub discussion or reach out on Twitter.

**Want to learn more?** Check out the [API documentation](https://github.com/ferasbusiness666/ReconForge/blob/main/docs/API.md) and [examples](https://github.com/ferasbusiness666/ReconForge/tree/main/examples).
