# Usage Guide

## Table of Contents

1. [Basic Commands](#basic-commands)
2. [Subdomain Discovery](#subdomain-discovery)
3. [Port Scanning](#port-scanning)
4. [Technology Detection](#technology-detection)
5. [Scope Checking](#scope-checking)
6. [Report Generation](#report-generation)
7. [Caching](#caching)
8. [Configuration](#configuration)
9. [Advanced Usage](#advanced-usage)

## Basic Commands

### Get Help

```bash
# General help
reconforge --help

# Help for specific command
reconforge subdomains --help
reconforge portscan --help
```

### Check Version

```bash
reconforge --version
```

## Subdomain Discovery

### Basic Subdomain Discovery

Discover subdomains using certificate transparency logs:

```bash
reconforge subdomains -d example.com
```

### With Caching

Reuse cached results if available:

```bash
# Use cache (default)
reconforge subdomains -d example.com

# Disable cache and force fresh query
reconforge subdomains -d example.com --no-cache
```

### Example Output

```
       Subdomains for example.com
┏━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Subdomain         ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 1  │ api.example.com   │
│ 2  │ login.example.com │
│ 3  │ www.example.com   │
│ 4  │ admin.example.com │
└────┴───────────────────┘
Total: 4
```

### Tips

- Results are deduplicated and sorted
- Wildcard prefixes are automatically removed
- Results are cached for 24 hours by default

## Port Scanning

### Basic Port Scan

Scan common ports (80, 443, 8080, 8443, 22, 21, 3306, 6379):

```bash
reconforge portscan -t api.example.com
```

### Concurrent vs Sequential

```bash
# Concurrent scanning (faster, default)
reconforge portscan -t api.example.com --concurrent

# Sequential scanning
reconforge portscan -t api.example.com --sequential
```

### Custom Timeout

```bash
# Increase timeout for slow networks
reconforge portscan -t api.example.com --timeout 5.0
```

### Example Output

```
            Port scan for api.example.com
┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Port ┃ Status    ┃ Banner / Note                   ┃
┡━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   80 │ 🟢 open   │ HTTP/1.1 301 Moved Permanently  │
│  443 │ 🟢 open   │ No banner                       │
│ 8080 │ 🔴 closed │ Connection refused              │
│   22 │ 🔴 closed │ Connection refused              │
└──────┴───────────┴─────────────────────────────────┘
```

### Tips

- Concurrent scanning is 4x faster than sequential
- Timeouts are per-port, not total
- DNS errors don't stop the scan (continues to next port)

## Technology Detection

### Basic Detection

Detect technologies on a URL:

```bash
reconforge techdetect -u https://api.example.com
```

### With Custom Timeout

```bash
reconforge techdetect -u https://api.example.com --timeout 15.0
```

### Example Output

```
Final URL: https://api.example.com/
HTTP status: 200

Detected Technologies
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Technology              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ nginx                   │
│ HSTS                    │
│ Content Security Policy │
└─────────────────────────┘

Interesting Headers
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Header                 ┃ Value                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Server                 │ nginx/1.19.0                            │
│ Strict-Transport-Sec... │ max-age=31536000; includeSubDomains    │
│ Content-Security-Poli... │ default-src 'self'; script-src 'self' │
└────────────────────────┴─────────────────────────────────────────┘
```

### Tips

- Detects 30+ technologies
- Analyzes headers, cookies, and response body
- Automatically follows redirects

## Scope Checking

### Create Scope Files

**targets.txt:**
```
api.example.com
login.example.com
thirdparty.net
192.0.2.50
```

**scope.txt:**
```
example.com
*.example.com
192.0.2.0/24
```

### Check Scope

```bash
reconforge scopecheck -t targets.txt -s scope.txt
```

### Example Output

```
In-Scope Targets
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Target            ┃ Reason                     ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ api.example.com   │ matched wildcard *.example.com │
│ 192.0.2.50        │ matched CIDR 192.0.2.0/24 │
└───────────────────┴────────────────────────────┘

Out-of-Scope Targets
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Target             ┃ Reason                ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ thirdparty.net     │ no scope rule matched │
└────────────────────┴───────────────────────┘
```

### Scope Rules

Supported scope rule formats:

- **Exact domain:** `example.com`
- **Wildcard:** `*.example.com`
- **Single IP:** `192.0.2.1`
- **CIDR range:** `192.0.2.0/24`

## Report Generation

### Generate Markdown Report

```bash
reconforge report -d example.com --output report.md
```

### Generate HTML Report

```bash
reconforge report -d example.com --output report.html --format html
```

### Generate JSON Report

```bash
reconforge report -d example.com --output report.json --format json
```

### Limit Hosts Scanned

```bash
# Scan only first 10 discovered subdomains
reconforge report -d example.com --output report.md --max-hosts 10
```

### Sequential Scanning

```bash
# Use sequential scanning instead of concurrent
reconforge report -d example.com --output report.md --sequential
```

### Example Report Structure

```markdown
# ReconForge Report: example.com

**Generated:** 2026-05-20 12:34:56 UTC
**Target domain:** `example.com`

## Summary

- Subdomains found: **4**
- Hosts scanned for ports: **4**
- Technology fingerprints collected: **4**

## Subdomains Found

- `api.example.com`
- `login.example.com`
- `www.example.com`
- `admin.example.com`

## Open Ports and Banners

### `api.example.com`

| Port | Status | Banner |
| --- | --- | --- |
| 80 | open | HTTP/1.1 301 Moved Permanently |
| 443 | open | No banner |

## Detected Technologies

### `https://api.example.com/`

- HTTP status: `200`
- Technologies: `nginx`, `HSTS`, `Content Security Policy`

| Header | Value |
| --- | --- |
| `Server` | `nginx/1.19.0` |
| `Strict-Transport-Security` | `max-age=31536000` |
```

## Caching

### View Cache Stats

```bash
reconforge cache-stats
```

### Clear Cache

```bash
reconforge cache-clear
```

### Disable Cache for Command

```bash
reconforge subdomains -d example.com --no-cache
```

## Configuration

### View Configuration

```bash
reconforge config-show
```

### Set Configuration Value

```bash
# Set timeout to 15 seconds
reconforge config-set --key timeout --value 15.0

# Disable concurrent scanning
reconforge config-set --key concurrent_scanning --value false

# Set max workers
reconforge config-set --key max_workers --value 8
```

### Configuration File

Edit `~/.reconforge/config.json` directly:

```json
{
  "timeout": 10.0,
  "port_scan_timeout": 2.0,
  "max_workers": 4,
  "concurrent_scanning": true,
  "cache_enabled": true,
  "cache_ttl": 86400,
  "verbose": false,
  "retry_attempts": 3,
  "retry_delay": 1.0
}
```

## Advanced Usage

### Workflow: Complete Recon

```bash
# 1. Discover subdomains
reconforge subdomains -d example.com > subdomains.txt

# 2. Check scope
reconforge scopecheck -t subdomains.txt -s scope.txt

# 3. Generate comprehensive report
reconforge report -d example.com --output report.md

# 4. Generate HTML for presentation
reconforge report -d example.com --output report.html --format html
```

### Workflow: Quick Assessment

```bash
# Single command to get everything
reconforge report -d example.com --output report.md --max-hosts 5
```

### Workflow: API Integration

```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()

# Discover subdomains
result = api.discover_subdomains("example.com")

# Process results
for subdomain in result["subdomains"]:
    tech = api.detect_technologies(f"https://{subdomain}")
    print(f"{subdomain}: {', '.join(tech['technologies'])}")
```

## Performance Tips

1. **Use concurrent scanning** - Default is faster for multiple ports
2. **Set appropriate timeouts** - Reduce for fast networks, increase for slow
3. **Enable caching** - Avoid redundant API calls
4. **Limit hosts scanned** - Use `--max-hosts` to focus on important targets
5. **Use sequential for single ports** - Faster for single port scans

## Troubleshooting

### Slow Subdomain Discovery

- Check internet connection
- Increase timeout: `--timeout 30.0`
- Try again later (crt.sh rate limits)

### Port Scan Timing Out

- Increase timeout: `--timeout 5.0`
- Use sequential mode: `--sequential`
- Check network connectivity

### Technology Detection Fails

- Check URL is accessible: `curl -I https://example.com`
- Increase timeout: `--timeout 20.0`
- Try HTTP instead of HTTPS

## Best Practices

1. **Always verify scope** - Use `scopecheck` before testing
2. **Start with subdomains** - Discover targets before scanning
3. **Use reports** - Generate reports for documentation
4. **Cache results** - Reuse results to save time
5. **Monitor errors** - Check error messages for issues

## Next Steps

- Read the [API Documentation](./API.md)
- Check [Installation Guide](./INSTALLATION.md)
- See [Contributing Guide](../CONTRIBUTING.md)
- Review [AI Triage Prompts](../prompts/ai_triage.md)
