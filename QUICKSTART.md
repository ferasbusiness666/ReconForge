# ReconForge Quick Start Guide

Get started with ReconForge in 5 minutes! 🚀

## Installation

### Option 1: From PyPI (Recommended)
```bash
pip install reconforge
```

### Option 2: From Source
```bash
git clone https://github.com/ferasbusiness666/ReconForge.git
cd ReconForge
pip install .
```

### Verify Installation
```bash
reconforge --version
# Output: reconforge, version 1.0.0
```

## Your First Scan (5 minutes)

### 1. Discover Subdomains
```bash
reconforge subdomains -d example.com
```

**Output:**
```
       Subdomains for example.com
┏━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Subdomain         ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ 1  │ api.example.com   │
│ 2  │ login.example.com │
│ 3  │ www.example.com   │
└────┴───────────────────┘
Total: 3
```

### 2. Scan for Open Ports
```bash
reconforge portscan -t api.example.com
```

**Output:**
```
            Port scan for api.example.com
┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Port ┃ Status    ┃ Banner / Note                   ┃
┡━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   80 │ 🟢 open   │ HTTP/1.1 301 Moved Permanently  │
│  443 │ 🟢 open   │ No banner                       │
│ 8080 │ 🔴 closed │ Connection refused              │
└──────┴───────────┴─────────────────────────────────┘
```

### 3. Detect Technologies
```bash
reconforge techdetect -u https://api.example.com
```

**Output:**
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
```

### 4. Generate Full Report
```bash
reconforge report -d example.com --output report.md
```

This creates a professional markdown report with all findings!

## Common Commands

### Scan with Caching (Faster!)
```bash
# First run: 5 minutes
reconforge subdomains -d example.com

# Second run: <1 second (cached!)
reconforge subdomains -d example.com
```

### Custom Ports
```bash
reconforge portscan -t example.com --ports 80,443,3000,5000
```

### Batch Processing
```bash
# Scan multiple domains from a file
reconforge batch-scan --input domains.txt --output results.json
```

### Check Scope
```bash
# Validate targets against your scope
reconforge scopecheck -t targets.txt -s scope.txt
```

### View Configuration
```bash
reconforge config-show
```

### Clear Cache
```bash
reconforge cache-clear
```

## Python API Usage

```python
from reconforge.api import ReconForgeAPI

# Initialize API
api = ReconForgeAPI()

# Discover subdomains
result = api.discover_subdomains("example.com")
print(f"Found {result['count']} subdomains")
for subdomain in result['subdomains']:
    print(f"  - {subdomain}")

# Scan ports
ports = api.scan_ports("api.example.com")
print(f"Open ports: {[p['port'] for p in ports['results'] if p['status'] == 'open']}")

# Detect technologies
tech = api.detect_technologies("https://api.example.com")
print(f"Technologies: {tech['technologies']}")

# Generate report
api.generate_report("example.com", "report.md")
```

## Tips & Tricks

### 1. Use Concurrent Scanning for Speed
```bash
# 4x faster port scanning
reconforge portscan -t example.com --concurrent
```

### 2. Export to JSON
```bash
reconforge report -d example.com --output report.json
```

### 3. View Help for Any Command
```bash
reconforge --help
reconforge subdomains --help
reconforge portscan --help
```

### 4. Chain Commands
```bash
# Discover subdomains, then scan each one
reconforge subdomains -d example.com | while read sub; do
  reconforge portscan -t $sub
done
```

## Troubleshooting

### "Command not found: reconforge"
```bash
# Make sure pip installed it correctly
pip install reconforge --force-reinstall

# Or use python module syntax
python -m reconforge.cli --help
```

### "Connection refused"
- Check your internet connection
- Verify the target is accessible
- Try with a timeout: `reconforge portscan -t example.com --timeout 30`

### "No subdomains found"
- The domain might not have public certificates
- Try a different domain
- Check if the domain exists: `nslookup example.com`

### "Permission denied"
- Some ports (<1024) require elevated privileges
- Try with `sudo` or use higher port numbers

## Next Steps

1. **Read the full documentation:** [docs/USAGE.md](docs/USAGE.md)
2. **Check out examples:** [examples/](examples/)
3. **Learn the API:** [docs/API.md](docs/API.md)
4. **Security best practices:** [docs/SECURITY.md](docs/SECURITY.md)

## Need Help?

- **FAQ:** [docs/FAQ.md](docs/FAQ.md)
- **GitHub Issues:** [Report bugs](https://github.com/ferasbusiness666/ReconForge/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/ferasbusiness666/ReconForge/discussions)

## Legal Notice

ReconForge is intended **only for systems you own or have explicit permission to test**. Always:
- Obtain written authorization before testing
- Follow program scope and rules of engagement
- Comply with all applicable laws
- Respect rate limits and terms of service

---

**Happy hunting! 🔍**

For more information, visit: https://github.com/ferasbusiness666/ReconForge
