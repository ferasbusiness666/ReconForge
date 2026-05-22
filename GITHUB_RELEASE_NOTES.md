# ReconForge v1.0.0 - Official Release 🎉

**The AI-assisted recon toolkit for bug bounty hunters and security researchers**

## 🚀 What is ReconForge?

ReconForge automates the reconnaissance phase of security assessments. In minutes, you can discover subdomains, scan ports, detect technologies, and generate professional reports.

**Installation:**
```bash
pip install reconforge
```

## ✨ Key Features

- 🔎 **Subdomain Discovery** - Find subdomains from certificate transparency data
- ⚡ **Concurrent Port Scanning** - 4x faster than sequential scanning
- 🧬 **Technology Detection** - Identify 30+ technologies from headers and responses
- 🧭 **Scope Checking** - Validate targets against exact hosts, wildcards, and CIDR blocks
- 📄 **Multiple Export Formats** - Markdown, JSON, HTML, CSV
- 💾 **Result Caching** - 100x faster repeated scans
- 🐍 **Python API** - Full programmatic access
- 🔄 **Batch Processing** - Scan multiple domains at once
- 📊 **Analysis Engine** - Risk assessment and vulnerability detection
- 🌐 **Web Server** - Optional dashboard for viewing reports

## 🎯 Quick Start

### Basic Usage
```bash
# Discover subdomains
reconforge subdomains -d example.com

# Scan ports
reconforge portscan -t api.example.com --concurrent

# Detect technologies
reconforge techdetect -u https://api.example.com

# Generate full report
reconforge report -d example.com --output report.md
```

### Python API
```python
from reconforge.api import ReconForgeAPI

api = ReconForgeAPI()
result = api.discover_subdomains("example.com")
print(f"Found {result['count']} subdomains")
```

## 📊 Performance

- **Subdomain Discovery:** ~1 minute for typical domains
- **Port Scanning:** 7 minutes for 50 hosts (concurrent) vs 30 minutes (sequential)
- **Caching:** 100x faster on repeated scans

## 🖥️ Compatibility

- **OS:** Linux, macOS, Windows
- **Python:** 3.9+
- **Dependencies:** click, rich, requests (automatically installed)

## 📚 Documentation

- [README](README.md) - Project overview
- [Installation Guide](docs/INSTALLATION.md) - Setup instructions
- [Usage Guide](docs/USAGE.md) - Detailed CLI usage
- [API Documentation](docs/API.md) - Python API reference
- [Security Guide](docs/SECURITY.md) - Best practices
- [FAQ](docs/FAQ.md) - Common questions
- [Examples](examples/) - Code examples

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Thanks

Built with ❤️ for the security research community.

---

**Ready to automate your recon?** Install now: `pip install reconforge`

**Have questions?** Check the [FAQ](docs/FAQ.md) or open a [GitHub discussion](https://github.com/ferasbusiness666/ReconForge/discussions).

**Found a bug?** Report it on [GitHub Issues](https://github.com/ferasbusiness666/ReconForge/issues).
