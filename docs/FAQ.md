# Frequently Asked Questions (FAQ)

## General Questions

### What is ReconForge?

ReconForge is an AI-assisted recon toolkit for bug bounty hunters and security researchers. It automates common reconnaissance tasks like subdomain discovery, port scanning, technology detection, and report generation.

### Who should use ReconForge?

ReconForge is designed for:
- Bug bounty hunters
- Security researchers
- Penetration testers
- System administrators
- DevSecOps engineers

### Is ReconForge free?

Yes! ReconForge is open-source and free to use under the MIT License.

### Can I use ReconForge commercially?

Yes, you can use ReconForge for commercial purposes. See the [LICENSE](../LICENSE) file for details.

## Installation & Setup

### How do I install ReconForge?

```bash
pip install reconforge
```

For development installation:
```bash
git clone https://github.com/ferasbusiness666/ReconForge.git
cd ReconForge
pip install -e .
```

### What are the system requirements?

- Python 3.9 or higher
- pip package manager
- 50 MB disk space
- Internet connection

### How do I verify the installation?

```bash
reconforge --version
reconforge --help
```

### Do I need to configure anything?

ReconForge works out of the box. Optional configuration can be done:

```bash
reconforge config-show
reconforge config-set --key timeout --value 15.0
```

## Usage Questions

### How do I scan a domain?

```bash
# Discover subdomains
reconforge subdomains -d example.com

# Scan ports
reconforge portscan -t api.example.com

# Detect technologies
reconforge techdetect -u https://api.example.com

# Generate full report
reconforge report -d example.com --output report.md
```

### How long does a scan take?

Scan time depends on:
- Number of subdomains (typically 1-5 minutes)
- Number of ports scanned (typically 30 seconds - 2 minutes)
- Network speed
- Target responsiveness

Use concurrent scanning for faster results:
```bash
reconforge portscan -t example.com --concurrent
```

### Can I scan multiple domains at once?

Yes, use the batch processing API:

```python
from reconforge.batch import BatchProcessor

processor = BatchProcessor()
results = processor.scan_domains(["example.com", "example.org"])
```

### How do I export results in different formats?

```bash
# Markdown (default)
reconforge report -d example.com --output report.md --format md

# JSON
reconforge report -d example.com --output report.json --format json

# HTML
reconforge report -d example.com --output report.html --format html
```

### Can I use ReconForge in my Python code?

Yes! Use the Python API:

```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()
result = api.discover_subdomains("example.com")
```

See [API Documentation](./API.md) for details.

## Performance & Optimization

### How can I speed up scans?

1. **Enable concurrent scanning** (default):
   ```bash
   reconforge portscan -t example.com --concurrent
   ```

2. **Use caching**:
   ```bash
   reconforge subdomains -d example.com  # Uses cache
   ```

3. **Limit hosts scanned**:
   ```bash
   reconforge report -d example.com --max-hosts 10
   ```

4. **Increase timeout for slow networks**:
   ```bash
   reconforge portscan -t example.com --timeout 5.0
   ```

### Why is subdomain discovery slow?

Subdomain discovery queries certificate transparency logs (crt.sh). Speed depends on:
- Network latency
- crt.sh server load
- Number of certificates for the domain

### Can I disable caching?

Yes:
```bash
reconforge subdomains -d example.com --no-cache
```

### How much disk space does caching use?

Check cache statistics:
```bash
reconforge cache-stats
```

Clear cache if needed:
```bash
reconforge cache-clear
```

## Features & Capabilities

### What subdomains does ReconForge find?

ReconForge queries certificate transparency logs (crt.sh) which contain:
- All publicly issued SSL certificates
- Subdomains from certificate SANs
- Historical certificate data

It does NOT find:
- Subdomains without certificates
- Internal/private subdomains
- Subdomains behind firewalls

### What ports does ReconForge scan?

By default, ReconForge scans common ports:
- 80, 443 (HTTP/HTTPS)
- 8080, 8443 (HTTP/HTTPS alt)
- 22 (SSH)
- 21 (FTP)
- 3306 (MySQL)
- 6379 (Redis)

Custom ports can be specified via the API.

### What technologies can ReconForge detect?

ReconForge detects 30+ technologies including:
- Web servers (nginx, Apache, IIS)
- Frameworks (React, Vue, Django, Flask)
- Languages (PHP, Python, Node.js, Java)
- Security headers (HSTS, CSP, X-Frame-Options)
- CDNs and WAFs
- And many more...

### Can ReconForge find vulnerabilities?

ReconForge identifies potential vulnerability indicators:
- Outdated software versions
- Missing security headers
- Exposed services
- Misconfigurations

However, it does NOT perform deep vulnerability scanning. Use specialized tools for that.

## Troubleshooting

### ReconForge command not found

**Solution:** Ensure ReconForge is installed:
```bash
pip install --upgrade reconforge
```

### SSL/Certificate errors

**Solution:** Update SSL certificates:
```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# Or use requests without SSL verification (not recommended)
```

### Slow network timeouts

**Solution:** Increase timeout:
```bash
reconforge subdomains -d example.com --timeout 30.0
```

### "Connection refused" errors

**Solution:** Check network connectivity:
```bash
ping example.com
curl https://example.com
```

### Cache not working

**Solution:** Clear cache and retry:
```bash
reconforge cache-clear
reconforge subdomains -d example.com
```

### Memory usage too high

**Solution:** Limit concurrent operations:
```bash
reconforge config-set --key max_workers --value 2
```

## Legal & Ethical

### Is it legal to use ReconForge?

ReconForge is legal to use for authorized testing. **Always obtain written permission** before testing any system you don't own.

### Can I use ReconForge for unauthorized testing?

**No.** Unauthorized access to computer systems is illegal under laws like the CFAA (US), GDPR (EU), and others.

### What should I do if I find a vulnerability?

1. Document the finding
2. Report to the organization
3. Give them time to fix (typically 90 days)
4. Don't share publicly until patched
5. Consider responsible disclosure programs

See [Security Best Practices](./SECURITY.md) for details.

### How do I report security issues in ReconForge?

Email security details to: [security contact when available]

Do not open public GitHub issues for security vulnerabilities.

## Contributing & Community

### How can I contribute to ReconForge?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Where can I report bugs?

Open an issue on [GitHub Issues](https://github.com/ferasbusiness666/ReconForge/issues)

### Where can I suggest features?

Open a discussion on [GitHub Discussions](https://github.com/ferasbusiness666/ReconForge/discussions)

### How can I get help?

1. Check the [README](../README.md)
2. Read the [Usage Guide](./USAGE.md)
3. Review [API Documentation](./API.md)
4. Open a GitHub discussion
5. Check existing issues

## Advanced Topics

### Can I integrate ReconForge with other tools?

Yes! ReconForge provides:
- CLI for shell scripting
- Python API for programmatic access
- JSON export for integration

Example:
```python
from reconforge.api import ReconForgeAPI
import subprocess

api = ReconForgeAPI()
result = api.discover_subdomains("example.com")

for subdomain in result["subdomains"]:
    subprocess.run(["nuclei", "-u", f"https://{subdomain}"])
```

### Can I schedule ReconForge scans?

Yes, using system tools:

```bash
# Linux/macOS: cron job
0 2 * * * /usr/local/bin/reconforge report -d example.com --output report.md

# Windows: Task Scheduler
```

Or use the Python API with a scheduler:

```python
from reconforge.api import ReconForgeAPI
import schedule
import time

def scan():
    api = ReconForgeAPI()
    api.generate_report("example.com", "report.md")

schedule.every().day.at("02:00").do(scan)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Can I use ReconForge in Docker?

Yes:

```dockerfile
FROM python:3.11

RUN pip install reconforge

ENTRYPOINT ["reconforge"]
```

Build and run:
```bash
docker build -t reconforge .
docker run reconforge subdomains -d example.com
```

## Still Have Questions?

- Check the [README](../README.md)
- Review [API Documentation](./API.md)
- Read [Usage Guide](./USAGE.md)
- Open a [GitHub Discussion](https://github.com/ferasbusiness666/ReconForge/discussions)
- Check [GitHub Issues](https://github.com/ferasbusiness666/ReconForge/issues)

---

**Last Updated:** May 2026
