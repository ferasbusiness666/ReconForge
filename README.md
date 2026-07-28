# ReconForge

```text
 ____  _____ ____ ___  _   _ _____ ___  ____   ____ _____
|  _ \| ____/ ___/ _ \| \ | |  ___/ _ \|  _ \ / ___| ____|
| |_) |  _|| |  | | | |  \| | |_ | | | | |_) | |  _|  _|
|  _ <| |__| |__| |_| | |\  |  _|| |_| |  _ <| |_| | |___
|_| \_\_____\____\___/|_| \_|_|   \___/|_| \_\\____|_____|
```

ReconForge is a lightweight, scope-aware recon toolkit for authorized bug bounty and security testing. It collects first-pass recon data, keeps output readable and scriptable, and generates reports without adding exploit automation or aggressive defaults.

## What ReconForge Is

- A safe first-pass collection and reporting layer.
- A scope-checking tool for reducing out-of-scope mistakes.
- A lightweight way to combine passive subdomains, bounded port checks, HTTP probing, GitHub metadata, and markdown/JSON output.

## What ReconForge Is Not

- It is not a vulnerability scanner or exploit tool.
- It does not replace Amass or subfinder for serious subdomain enumeration.
- It does not replace httpx for large-scale HTTP probing.
- It does not replace naabu or nmap for comprehensive port scanning.
- It does not replace nuclei or manual validation for vulnerability checks.

## Features

- Subdomain discovery from public sources: crt.sh, HackerTarget hostsearch, and Cert Spotter.
- Bounded concurrent TCP checks with safe, normal, and explicitly opt-in deep profiles.
- Clear port statuses: `open`, `closed`, `filtered/timeout`, and `error`.
- HTTP technology detection from headers, cookies, security headers, CDN hints, and light body fingerprints.
- Scope checking for exact hosts, wildcard domains, IP addresses, and CIDR ranges.
- GitHub repository recon from the public GitHub API, with optional `GITHUB_TOKEN` support.
- Bounded concurrent HTTP/HTTPS probing for saved host lists.
- Markdown reports with collection notes when providers fail.
- Optional JSON output for automation.
- Optional scope notes in markdown reports.
- Optional scan profiles and custom port lists.
- AI-ready report summaries without requiring an AI API key.
- Rich terminal tables with Windows-safe status lines.

## Installation

### Option A: Normal CLI Install With pipx

Use this when you want `reconforge` to keep working after closing CMD or PowerShell without manually activating `.venv`.

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
pipx install .
reconforge --help
reconforge --version
```

If your Python Scripts directory is not on PATH, you can still run:

```powershell
py -m reconforge --help
```

Linux/macOS:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install .
reconforge --help
```

### Option B: Optional Isolated Dev Install

`.venv` is optional. Use it when you want project dependencies isolated from your main Python install.

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
reconforge --help
```

If you use `.venv`, activate it again in every new CMD or PowerShell session before running `reconforge`:

```powershell
.venv\Scripts\activate
```

If you do not want to activate `.venv` after closing CMD, use Option A instead.

### Troubleshooting: `reconforge` Is Not Recognized

If Windows prints `'reconforge' is not recognized`:

- Make sure installation completed without errors.
- If using pipx, try `pipx ensurepath`, then open a new terminal.
- Try reinstalling from the project folder: `py -m pip install -e .`
- Try the module entrypoint: `py -m reconforge --help`
- Check that your Python Scripts directory is on PATH.
- If you installed inside `.venv`, activate it first: `.venv\Scripts\activate`

## Usage

### Discover Subdomains

```powershell
reconforge subdomains -d example.com
reconforge subdomains -d example.com --json
reconforge subdomains -d example.com --output subdomains.txt
```

### Scan Common Ports

```powershell
reconforge portscan -t example.com
reconforge portscan -t example.com --profile normal
reconforge portscan -t example.com --profile deep
reconforge portscan -t example.com --ports 80,443,3000
reconforge portscan -t example.com --workers 8
reconforge portscan -t example.com --json
```

Profiles:

- `safe`: small default list.
- `normal`: adds common app/dev ports.
- `deep`: larger bounded common-service list. This is opt-in and is not a full port range scan.

### Detect Technologies

```powershell
reconforge techdetect -u https://example.com
reconforge techdetect -u https://example.com --json
reconforge techdetect -u https://example.com --output tech.json
```

### Probe HTTP/HTTPS

```powershell
reconforge httpprobe -i subdomains.txt
reconforge httpprobe -i subdomains.txt --workers 8
reconforge httpprobe -i subdomains.txt --json
reconforge httpprobe -i subdomains.txt --output http.json
```

This checks HTTP/HTTPS reachability only. It does not crawl or brute-force paths.

### Check Scope

```powershell
reconforge scopecheck -t targets.txt -s scope.txt
reconforge scopecheck -t targets.txt -s scope.txt --json
reconforge scopecheck -t targets.txt -s scope.txt --output scope.json
```

Example `scope.txt`:

```text
example.com
*.example.com
192.0.2.0/24
```

### GitHub Repository Recon

Owner or organization mode:

```powershell
reconforge github -o microsoft
reconforge github -o microsoft --json
reconforge github -o microsoft --output github.json
```

Repo-specific mode:

```powershell
reconforge github -o microsoft -r vscode
reconforge github -o microsoft -r vscode --json
```

ReconForge works without authentication for public repositories. For higher GitHub API limits, set `GITHUB_TOKEN` in your environment. ReconForge uses the token only in the API header and never prints it.

### Generate a Report

```powershell
reconforge report -d example.com --output reports/example.md
```

Include GitHub recon:

```powershell
reconforge report -d example.com --github-owner example --output reports/example.md
```

Include one GitHub repo:

```powershell
reconforge report -d example.com --github-owner microsoft --github-repo vscode --output reports/example.md
```

Include scope notes:

```powershell
reconforge report -d example.com --scope scope.txt --output reports/example.md
```

Print a JSON summary while still writing the markdown report:

```powershell
reconforge report -d example.com --output reports/example.md --json
```

Build a markdown report from saved JSON findings:

```powershell
reconforge report --from-json recon.json --output reports/example.md
```

The report command creates missing output folders automatically and writes collection errors under `Collection Notes` instead of crashing.

### Create an AI-Ready Summary

```powershell
reconforge summarize --report reports/example.md
reconforge summarize --report reports/example.md --output prompt-summary.txt
reconforge summarize --report reports/example.md --json
```

This does not call an AI API. It creates a compact text summary you can paste into your own AI tool after removing anything sensitive.

### Config File

ReconForge can read optional defaults from `reconforge.json` in the current folder.

```json
{
  "portscan": {
    "profile": "normal",
    "ports": [80, 443, 3000],
    "timeout": 2.0,
    "workers": 8
  }
}
```

Command-line options override config values.

## GitHub Recon Notes

GitHub recon collects public metadata only:

- Repository name, description, URL, stars, forks, language, default branch, updated date.
- Archived, private, and fork flags when available from the API.
- Interesting files such as `README.md`, `package.json`, `requirements.txt`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `.env.example`, and `.github/workflows/*.yml`.
- Basic tech and recon notes such as Docker usage, CI/CD workflows, environment examples, Python/Node/Rust/Go indicators, frontend framework indicators, and possible deployment files.

ReconForge does not claim vulnerabilities from metadata alone. Treat these notes as leads to validate manually.

## Recommended Toolchain

ReconForge is designed to work alongside mature tools:

```text
subfinder / Amass
        |
        v
reconforge scopecheck
        |
        v
reconforge httpprobe
        |
        v
httpx / naabu / nmap
        |
        v
nuclei and manual validation
```

Use ReconForge for scope-aware first-pass collection and reports. Use the specialized tools for deeper, high-scale work.

## AI Triage Prompts

The prompt library lives in `prompts/ai_triage.md`. Use it for a structured second pass over:

- HTTP responses and headers.
- Authentication, SSO, MFA, and session flows.
- Sensitive or admin-looking endpoints.
- JavaScript routes, feature flags, and source maps.
- API authorization and object-level access patterns.
- Parameter behavior and anomaly triage.
- Finding prioritization and report drafting.

Remove secrets, tokens, personal data, and proprietary content before pasting material into any AI system.

## Project Structure

```text
reconforge/
  __init__.py
  __main__.py
  cli.py
  config.py
  github_recon.py
  httpprobe.py
  output.py
  portscan.py
  report.py
  scopecheck.py
  summarize.py
  subdomains.py
  techdetect.py
tests/
  test_core.py
prompts/
  ai_triage.md
examples/
  example_report.md
  reconforge.json
requirements.txt
pyproject.toml
setup.py
README.md
```

## Checks

```powershell
py -m compileall reconforge
py -m unittest discover -s tests
reconforge --help
reconforge github --help
reconforge httpprobe --help
reconforge report --help
reconforge summarize --help
```

## Authorized Testing Only

ReconForge is intended only for systems you own or have explicit permission to test. You are responsible for following program scope, laws, terms of service, and rate limits. Do not use ReconForge against unauthorized targets.

## License

MIT. See `LICENSE`.
