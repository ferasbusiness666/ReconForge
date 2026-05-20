# ReconForge API Documentation

## Overview

ReconForge provides a comprehensive Python API for programmatic access to all recon capabilities. Use it to integrate recon workflows into your own tools and scripts.

## Installation

```bash
pip install reconforge
```

## Quick Start

```python
from reconforge.api import ReconForgeAPI

# Initialize API
api = ReconForgeAPI()

# Discover subdomains
result = api.discover_subdomains("example.com")
print(f"Found {result['count']} subdomains")

# Scan ports
ports = api.scan_ports("api.example.com")
print(f"Open ports: {[r['port'] for r in ports['results'] if r['status'] == 'open']}")

# Detect technologies
tech = api.detect_technologies("https://api.example.com")
print(f"Technologies: {tech['technologies']}")

# Generate report
api.generate_report("example.com", "report.md")
```

## API Reference

### ReconForgeAPI Class

Main class for all recon operations.

#### Initialization

```python
api = ReconForgeAPI(use_cache=True, log_file=None)
```

**Parameters:**
- `use_cache` (bool): Enable result caching (default: True)
- `log_file` (str): Optional path to log file

#### Methods

### discover_subdomains()

Discover subdomains for a domain using certificate transparency logs.

```python
result = api.discover_subdomains(domain, timeout=None)
```

**Parameters:**
- `domain` (str): Target domain
- `timeout` (float): Request timeout in seconds (uses config default if None)

**Returns:**
```python
{
    "domain": "example.com",
    "subdomains": ["api.example.com", "www.example.com", ...],
    "errors": [],
    "count": 42
}
```

**Example:**
```python
result = api.discover_subdomains("example.com")
for subdomain in result["subdomains"]:
    print(subdomain)
```

### scan_ports()

Scan common ports on a target host.

```python
result = api.scan_ports(host, ports=None, timeout=None, concurrent=None)
```

**Parameters:**
- `host` (str): Target hostname or IP
- `ports` (list): List of ports to scan (uses defaults if None)
- `timeout` (float): Socket timeout in seconds
- `concurrent` (bool): Use concurrent scanning

**Returns:**
```python
{
    "host": "api.example.com",
    "results": [
        {
            "host": "api.example.com",
            "port": 80,
            "status": "open",
            "banner": "HTTP/1.1 301 Moved Permanently"
        },
        ...
    ],
    "errors": []
}
```

**Example:**
```python
result = api.scan_ports("api.example.com")
for port_info in result["results"]:
    if port_info["status"] == "open":
        print(f"Port {port_info['port']} is open")
```

### detect_technologies()

Detect web technologies on a URL.

```python
result = api.detect_technologies(url, timeout=None)
```

**Parameters:**
- `url` (str): Target URL
- `timeout` (float): Request timeout in seconds

**Returns:**
```python
{
    "url": "https://api.example.com/",
    "status_code": 200,
    "technologies": ["nginx", "HSTS", "Content Security Policy"],
    "headers": {
        "Server": "nginx/1.19.0",
        "Strict-Transport-Security": "max-age=31536000"
    },
    "errors": []
}
```

**Example:**
```python
result = api.detect_technologies("https://api.example.com")
print(f"Detected: {', '.join(result['technologies'])}")
```

### check_scope()

Validate targets against a scope file.

```python
result = api.check_scope(targets_file, scope_file)
```

**Parameters:**
- `targets_file` (str): Path to targets file (one per line)
- `scope_file` (str): Path to scope file (one rule per line)

**Returns:**
```python
{
    "in_scope": [
        {"target": "api.example.com", "reason": "matched wildcard *.example.com"},
        ...
    ],
    "out_of_scope": [
        {"target": "thirdparty.net", "reason": "no scope rule matched"},
        ...
    ],
    "errors": []
}
```

**Example:**
```python
result = api.check_scope("targets.txt", "scope.txt")
print(f"In scope: {len(result['in_scope'])}")
print(f"Out of scope: {len(result['out_of_scope'])}")
```

### generate_report()

Generate a comprehensive recon report.

```python
result = api.generate_report(domain, output, timeout=None, max_hosts=None, concurrent=None)
```

**Parameters:**
- `domain` (str): Target domain
- `output` (str): Output file path
- `timeout` (float): Request timeout in seconds
- `max_hosts` (int): Maximum hosts to scan
- `concurrent` (bool): Use concurrent scanning

**Returns:**
```python
{
    "output": "report.md",
    "hosts": ["api.example.com", "www.example.com"],
    "errors": []
}
```

**Example:**
```python
result = api.generate_report("example.com", "report.md")
print(f"Report written to {result['output']}")
```

### get_cache_stats()

Get cache statistics.

```python
stats = api.get_cache_stats()
```

**Returns:**
```python
{
    "total_entries": 42,
    "cache_size_bytes": 12345,
    "cache_path": "/home/user/.reconforge/cache/reconforge.db"
}
```

### clear_cache()

Clear all cached results.

```python
api.clear_cache()
```

### cleanup_expired_cache()

Remove expired cache entries.

```python
count = api.cleanup_expired_cache()
print(f"Cleaned up {count} entries")
```

## Configuration

ReconForge uses a configuration file at `~/.reconforge/config.json`. You can modify settings programmatically:

```python
from reconforge.config import get_config

config = get_config()
config.set("timeout", 15.0)
config.set("concurrent_scanning", True)
config.save()
```

**Available settings:**
- `timeout`: Default request timeout (seconds)
- `port_scan_timeout`: Port scan timeout (seconds)
- `max_workers`: Maximum concurrent threads
- `concurrent_scanning`: Enable concurrent scanning by default
- `cache_enabled`: Enable caching
- `cache_ttl`: Cache time-to-live (seconds)
- `verbose`: Verbose output
- `retry_attempts`: Number of retry attempts
- `retry_delay`: Delay between retries (seconds)

## Caching

ReconForge automatically caches results to speed up repeated operations. Cache is stored in `~/.reconforge/cache/reconforge.db`.

```python
# Disable caching for a specific operation
api = ReconForgeAPI(use_cache=False)

# Clear cache
api.clear_cache()

# Get cache stats
stats = api.get_cache_stats()
print(f"Cache size: {stats['cache_size_bytes']} bytes")
```

## Logging

Enable logging to see detailed operation information:

```python
api = ReconForgeAPI(log_file="/tmp/reconforge.log")
```

## Error Handling

All API methods return error information in the `errors` list:

```python
result = api.discover_subdomains("invalid")
if result["errors"]:
    for error in result["errors"]:
        print(f"Error: {error}")
```

## Examples

### Complete Recon Workflow

```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()

# 1. Discover subdomains
print("Discovering subdomains...")
subdomains = api.discover_subdomains("example.com")
print(f"Found {subdomains['count']} subdomains")

# 2. Scan ports on each subdomain
print("\nScanning ports...")
for subdomain in subdomains["subdomains"][:5]:  # Limit to first 5
    ports = api.scan_ports(subdomain)
    open_ports = [r for r in ports["results"] if r["status"] == "open"]
    if open_ports:
        print(f"{subdomain}: {[p['port'] for p in open_ports]}")

# 3. Detect technologies
print("\nDetecting technologies...")
for subdomain in subdomains["subdomains"][:5]:
    tech = api.detect_technologies(f"https://{subdomain}")
    if tech["technologies"]:
        print(f"{subdomain}: {', '.join(tech['technologies'])}")

# 4. Generate report
print("\nGenerating report...")
api.generate_report("example.com", "report.md")
```

### Batch Processing

```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()

domains = ["example.com", "example.org", "example.net"]

for domain in domains:
    print(f"Processing {domain}...")
    result = api.discover_subdomains(domain)
    print(f"  Found {result['count']} subdomains")
    
    # Generate report
    api.generate_report(domain, f"{domain}_report.md")
```

### Integration with Other Tools

```python
from reconforge.api import ReconForgeAPI
import json

api = ReconForgeAPI()

# Get results as JSON for integration
result = api.discover_subdomains("example.com")

# Save as JSON
with open("subdomains.json", "w") as f:
    json.dump(result, f, indent=2)

# Use in another tool
for subdomain in result["subdomains"]:
    # Pass to your security scanner
    run_security_scan(subdomain)
```

## Best Practices

1. **Use caching** - Enable caching to avoid redundant API calls
2. **Handle errors** - Always check the `errors` list in responses
3. **Set appropriate timeouts** - Adjust timeouts based on network conditions
4. **Use concurrent scanning** - Enable for faster results on multiple ports
5. **Clean up cache** - Periodically call `cleanup_expired_cache()`
6. **Log important operations** - Enable logging for debugging

## Troubleshooting

### Cache not working
```python
# Clear cache and retry
api.clear_cache()
result = api.discover_subdomains("example.com")
```

### Slow performance
```python
# Enable concurrent scanning
result = api.scan_ports("example.com", concurrent=True)
```

### Network timeouts
```python
# Increase timeout
result = api.discover_subdomains("example.com", timeout=30.0)
```

## License

MIT License - See LICENSE file for details
