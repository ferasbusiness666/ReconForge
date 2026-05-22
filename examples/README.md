# ReconForge Examples

This directory contains practical examples of using ReconForge for various recon tasks.

## Quick Start

All examples use the ReconForge Python API. Make sure ReconForge is installed:

```bash
pip install reconforge
```

## Examples

### 1. Basic Scan (`basic_scan.py`)

Simple example showing how to:
- Discover subdomains
- Scan ports
- Detect technologies

```bash
python examples/basic_scan.py
```

**Output:**
```
Scanning example.com...

1. Discovering subdomains...
Found 42 subdomains:
  - api.example.com
  - www.example.com
  ...

2. Scanning ports on api.example.com...
Found 2 open ports:
  - Port 80: HTTP/1.1 301 Moved Permanently
  - Port 443: No banner

3. Detecting technologies on api.example.com...
Status: 200
Technologies: nginx, HSTS, Content Security Policy

Done!
```

### 2. Advanced Analysis (`advanced_analysis.py`)

Example showing how to:
- Analyze subdomain patterns
- Summarize open ports
- Assess security posture
- Generate risk scores

```bash
python examples/advanced_analysis.py
```

**Output:**
```
Advanced analysis for example.com
============================================================

1. SUBDOMAIN STATISTICS
------------------------------------------------------------
Total subdomains: 42
Unique prefixes: 35
Common prefixes:
  - api: 5
  - www: 3
  ...

2. OPEN PORTS SUMMARY
------------------------------------------------------------
Total open ports: 8
Unique ports: 4
Open ports:
  - Port 80: 3 host(s)
  - Port 443: 3 host(s)
  ...

6. RISK ASSESSMENT
------------------------------------------------------------
Risk Score: 35/100
Risk Level: Medium
Key Findings:
  - Missing multiple security headers
  - Found 2 potential vulnerability indicators
```

### 3. Batch Processing (`batch_scan.py`)

Example showing how to:
- Scan multiple domains at once
- Process domains from a file
- Generate batch reports

```bash
python examples/batch_scan.py
```

**Output:**
```
Batch Scan Example
============================================================

Scanning 3 domains...

Batch Scan Summary:
------------------------------------------------------------
Timestamp: 2026-05-20T12:34:56.789123+00:00
Total Domains: 3
Successful: 3
Failed: 0

PER-DOMAIN RESULTS
------------------------------------------------------------
example.com: ✓
  Subdomains: 42
  Ports scanned: 15
  Technologies: 8
example.org: ✓
  Subdomains: 28
  Ports scanned: 12
  Technologies: 6
example.net: ✓
  Subdomains: 35
  Ports scanned: 14
  Technologies: 7
```

## Common Patterns

### Pattern 1: Custom Configuration

```python
from reconforge.config import get_config
from reconforge.api import ReconForgeAPI

# Customize configuration
config = get_config()
config.set("timeout", 15.0)
config.set("concurrent_scanning", True)
config.set("max_workers", 8)
config.save()

# Use API with custom config
api = ReconForgeAPI()
result = api.discover_subdomains("example.com")
```

### Pattern 2: Error Handling

```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()
result = api.discover_subdomains("example.com")

# Check for errors
if result["errors"]:
    print("Errors occurred:")
    for error in result["errors"]:
        print(f"  - {error}")

# Process results
print(f"Found {result['count']} subdomains")
```

### Pattern 3: Caching

```python
from reconforge.api import ReconForgeAPI
from reconforge.cache import get_cache

# Use caching
api = ReconForgeAPI(use_cache=True)

# First call - fetches from API
result1 = api.discover_subdomains("example.com")

# Second call - uses cache
result2 = api.discover_subdomains("example.com")

# View cache stats
cache = get_cache()
stats = cache.get_stats()
print(f"Cache size: {stats['cache_size_bytes']} bytes")

# Clear cache if needed
cache.clear()
```

### Pattern 4: Logging

```python
from reconforge.api import ReconForgeAPI

# Enable logging to file
api = ReconForgeAPI(log_file="/tmp/reconforge.log")

# Operations are logged
result = api.discover_subdomains("example.com")

# Check log file
with open("/tmp/reconforge.log", "r") as f:
    print(f.read())
```

### Pattern 5: Integration with Other Tools

```python
from reconforge.api import ReconForgeAPI
import subprocess

api = ReconForgeAPI()

# Get subdomains
result = api.discover_subdomains("example.com")

# Pass to another tool
for subdomain in result["subdomains"]:
    # Example: Run security scanner
    subprocess.run(["nuclei", "-u", f"https://{subdomain}"])
```

## Advanced Examples

### Workflow: Complete Security Assessment

```python
from reconforge.api import ReconForgeAPI
from reconforge.analyzer import FindingsAnalyzer

api = ReconForgeAPI()

# 1. Discover all subdomains
print("Step 1: Discovering subdomains...")
subdomains = api.discover_subdomains("example.com")

# 2. Scan all for ports
print("Step 2: Scanning ports...")
port_results = {}
for subdomain in subdomains["subdomains"]:
    ports = api.scan_ports(subdomain)
    port_results[subdomain] = ports["results"]

# 3. Detect technologies
print("Step 3: Detecting technologies...")
tech_results = {}
for subdomain in subdomains["subdomains"]:
    tech = api.detect_technologies(f"https://{subdomain}")
    tech_results[f"https://{subdomain}"] = tech

# 4. Analyze findings
print("Step 4: Analyzing findings...")
findings = {
    "subdomains": subdomains["subdomains"],
    "ports": port_results,
    "technologies": tech_results,
}
analyzer = FindingsAnalyzer(findings)

# 5. Generate assessment
risk = analyzer.get_risk_assessment()
print(f"\nRisk Score: {risk['risk_score']}/100")
print(f"Risk Level: {risk['risk_level']}")

# 6. Generate report
print("Step 5: Generating report...")
api.generate_report("example.com", "security_assessment.md")
print("Report saved to security_assessment.md")
```

### Workflow: Continuous Monitoring

```python
from reconforge.api import ReconForgeAPI
from reconforge.batch import BatchProcessor
from reconforge.compare import ScanComparator
import json
from datetime import datetime

processor = BatchProcessor()
api = ReconForgeAPI()

# First scan
print("Initial scan...")
results1 = processor.scan_domains(["example.com"], "scan1.json")

# Later: Second scan
print("Follow-up scan...")
results2 = processor.scan_domains(["example.com"], "scan2.json")

# Compare results
print("Comparing scans...")
with open("scan1.json") as f:
    scan1 = json.load(f)
with open("scan2.json") as f:
    scan2 = json.load(f)

comparator = ScanComparator(scan1["domains"][0], scan2["domains"][0])
changes = comparator.get_changes_summary()

print(f"Total changes: {changes['total_changes']}")
print(f"New subdomains: {changes['subdomains']['new_count']}")
print(f"New ports: {changes['ports']['new_count']}")

# Generate diff report
diff_report = comparator.generate_diff_report()
print(diff_report)
```

## Tips & Tricks

1. **Use concurrent scanning** - It's 4x faster for multiple ports
2. **Enable caching** - Avoid redundant API calls
3. **Set appropriate timeouts** - Adjust for your network
4. **Handle errors gracefully** - Always check the errors list
5. **Use logging** - Debug issues with detailed logs
6. **Batch similar operations** - Process multiple domains together

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'reconforge'"

**Solution:** Install ReconForge first:
```bash
pip install reconforge
```

### Issue: Slow performance

**Solution:** Enable concurrent scanning:
```python
api = ReconForgeAPI()
result = api.scan_ports("example.com", concurrent=True)
```

### Issue: Network timeouts

**Solution:** Increase timeout:
```python
result = api.discover_subdomains("example.com", timeout=30.0)
```

## Next Steps

- Read the [API Documentation](../docs/API.md)
- Check the [Usage Guide](../docs/USAGE.md)
- Explore the [CLI](../README.md#usage)
- Join the community on GitHub

## Contributing

Have a cool example? Submit a pull request!

1. Create a new Python file in this directory
2. Add a docstring explaining what it does
3. Include comments for clarity
4. Update this README with your example

## License

All examples are licensed under the MIT License.
