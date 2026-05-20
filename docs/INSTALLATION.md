# Installation Guide

## System Requirements

- Python 3.9 or higher
- pip or conda package manager
- 50 MB disk space for installation
- Internet connection for initial setup

## Installation Methods

### Method 1: pip (Recommended)

```bash
pip install reconforge
```

### Method 2: From Source

```bash
git clone https://github.com/ferasbusiness666/ReconForge.git
cd ReconForge
pip install .
```

### Method 3: Development Installation

For development and contributing:

```bash
git clone https://github.com/ferasbusiness666/ReconForge.git
cd ReconForge
pip install -r requirements-dev.txt
pip install -e .
```

## Verification

Verify the installation:

```bash
reconforge --version
reconforge --help
```

Expected output:
```
ReconForge - AI-assisted recon toolkit for bug bounty hunters
Usage: reconforge [OPTIONS] COMMAND [ARGS]...
```

## Platform-Specific Instructions

### macOS

```bash
# Using Homebrew
brew install python3
pip3 install reconforge

# Or manually
python3 -m pip install reconforge
```

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.9+
sudo apt-get update
sudo apt-get install python3.9 python3-pip

# Install ReconForge
pip3 install reconforge
```

### Linux (CentOS/RHEL)

```bash
# Install Python 3.9+
sudo yum install python39 python39-pip

# Install ReconForge
pip3.9 install reconforge
```

### Windows

```bash
# Using PowerShell
python -m pip install reconforge

# Or using Command Prompt
pip install reconforge
```

## Virtual Environment Setup (Recommended)

Using a virtual environment isolates ReconForge from other Python packages:

### Using venv

```bash
# Create virtual environment
python3 -m venv reconforge-env

# Activate it
# On macOS/Linux:
source reconforge-env/bin/activate
# On Windows:
reconforge-env\Scripts\activate

# Install ReconForge
pip install reconforge
```

### Using conda

```bash
# Create environment
conda create -n reconforge python=3.11

# Activate it
conda activate reconforge

# Install ReconForge
pip install reconforge
```

## Troubleshooting

### Issue: "Command not found: reconforge"

**Solution:** Ensure pip installed the command correctly:

```bash
# Reinstall
pip install --force-reinstall reconforge

# Or use Python module
python -m reconforge.cli --help
```

### Issue: "Permission denied" on Linux/macOS

**Solution:** Use `--user` flag or virtual environment:

```bash
# Option 1: Install for current user
pip install --user reconforge

# Option 2: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install reconforge
```

### Issue: "ModuleNotFoundError: No module named 'reconforge'"

**Solution:** Reinstall in the correct Python environment:

```bash
# Check Python version
python --version

# Reinstall
pip install --upgrade reconforge
```

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:** Update SSL certificates:

```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# Or disable SSL verification (not recommended)
pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org reconforge
```

### Issue: "No module named 'click' or 'rich'"

**Solution:** Install missing dependencies:

```bash
pip install --upgrade reconforge
```

### Issue: Slow installation

**Solution:** Use a faster PyPI mirror:

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ reconforge
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade reconforge
```

## Uninstallation

To remove ReconForge:

```bash
pip uninstall reconforge
```

## Configuration

After installation, ReconForge creates a configuration directory:

```bash
~/.reconforge/
├── config.json          # Configuration file
└── cache/
    └── reconforge.db    # Cache database
```

View current configuration:

```bash
reconforge config-show
```

## Next Steps

1. **Read the README**: `reconforge --help`
2. **Try basic commands**: `reconforge subdomains -d example.com`
3. **Check the documentation**: See `docs/` directory
4. **Join the community**: Report issues on GitHub

## Support

For issues or questions:

1. Check [GitHub Issues](https://github.com/ferasbusiness666/ReconForge/issues)
2. Read the [README](../README.md)
3. Check the [API Documentation](./API.md)
4. Open a new issue with details

## License

ReconForge is licensed under the MIT License. See LICENSE file for details.
