# ReconForge

```text
 ____  _____ ____ ___  _   _ _____ ___  ____   ____ _____
|  _ \| ____/ ___/ _ \| \ | |  ___/ _ \|  _ \ / ___| ____|
| |_) |  _|| |  | | | |  \| | |_ | | | | |_) | |  _|  _|
|  _ <| |__| |__| |_| | |\  |  _|| |_| |  _ <| |_| | |___
|_| \_\_____\____\___/|_| \_|_|   \___/|_| \_\\____|_____|
```

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](#installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![Stars](https://img.shields.io/github/stars/example/reconforge?style=social)](#reconforge)

**AI-assisted recon toolkit for bug bounty hunters**

ReconForge combines practical recon automation with AI triage prompts so authorized testers can move from raw findings to prioritized hypotheses faster.

## Features

- 🔎 **Subdomain discovery** from certificate transparency data via crt.sh.
- 🚪 **Common port scanning** for 80, 443, 8080, 8443, 22, 21, 3306, and 6379.
- 🧬 **Technology detection** from HTTP headers, cookies, security headers, CDN hints, and lightweight body signals.
- 🧭 **Scope checking** for exact hosts, wildcard domains, IP addresses, and CIDR ranges.
- 📄 **Markdown reports** with subdomains, open ports, banners, technology fingerprints, and collection notes.
- 🤖 **AI triage prompts** for HTTP responses, auth flows, JavaScript, APIs, sensitive endpoints, and prioritization.
- 🎨 **Rich terminal output** with tables, status indicators, and progress spinners.

## Installation

### Install with pip from a local checkout

```bash
git clone https://github.com/example/reconforge.git
cd reconforge
python -m pip install .
```

### Development install

```bash
git clone https://github.com/example/reconforge.git
cd reconforge
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Usage

### Discover subdomains

```bash
reconforge subdomains -d example.com
```

Sample output:

```text
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

### Scan common ports

```bash
reconforge portscan -t sub.example.com
```

Sample output:

```text
            Port scan for sub.example.com
┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Port ┃ Status    ┃ Banner / Note                   ┃
┡━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   80 │ 🟢 open   │ HTTP/1.1 301 Moved Permanently  │
│  443 │ 🟢 open   │ No banner                       │
│ 8080 │ 🔴 closed │ Connection refused              │
└──────┴───────────┴─────────────────────────────────┘
```

### Detect technologies

```bash
reconforge techdetect -u https://sub.example.com
```

Sample output:

```text
Final URL: https://sub.example.com/
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

### Check scope

```bash
reconforge scopecheck -t targets.txt -s scope.txt
```

Example `scope.txt`:

```text
example.com
*.example.com
192.0.2.0/24
```

Sample output:

```text
In-Scope Targets
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Target            ┃ Reason                     ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ api.example.com   │ matched wildcard *.example.com │
└───────────────────┴────────────────────────────┘

Out-of-Scope Targets
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Target             ┃ Reason                ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ thirdparty.net     │ no scope rule matched │
└────────────────────┴───────────────────────┘
```

### Generate a report

```bash
reconforge report -d example.com --output report.md
```

Sample output:

```text
Report written: report.md
```

See [`examples/example_report.md`](examples/example_report.md) for a realistic sample report.

## Why ReconForge?

### Avoid out-of-scope mistakes

Bug bounty scope can include exact hosts, wildcard subdomains, and IP ranges while excluding adjacent third-party systems. ReconForge's scope checker separates in-scope and out-of-scope targets before testing so you can fail safely and document why a target was included or excluded.

### Reduce manual recon time waste

Manual recon often means jumping between CT logs, socket checks, browser tabs, notes, and markdown templates. ReconForge gives you a small, auditable workflow for common first-pass tasks and produces tables that are easy to copy into notes or reports.

### Bring AI into recon without replacing judgment

ReconForge includes model-agnostic AI triage prompts that help analyze HTTP responses, unusual headers, auth flows, sensitive endpoints, JavaScript, API behavior, parameter anomalies, and prioritization. The prompts are designed to turn raw evidence into next-step hypotheses while keeping final validation in the tester's hands.

## AI Triage Prompts

The prompt library lives in [`prompts/ai_triage.md`](prompts/ai_triage.md). Use it when you need a structured second pass over:

- HTTP responses and headers.
- Authentication, SSO, MFA, and session flows.
- Sensitive or admin-looking endpoints.
- JavaScript routes, feature flags, and source maps.
- API authorization and object-level access patterns.
- Parameter behavior and anomaly triage.
- Finding prioritization and report drafting.

Always remove secrets, tokens, personal data, and proprietary content before pasting material into any AI system.

## Project Structure

```text
reconforge/
  __init__.py
  cli.py
  subdomains.py
  portscan.py
  techdetect.py
  scopecheck.py
  report.py
prompts/
  ai_triage.md
examples/
  example_report.md
requirements.txt
setup.py
README.md
```

## Contributing

Pull requests are welcome. For a smooth contribution:

1. Open an issue or describe the problem your PR solves.
2. Keep changes focused and include clear user-facing errors.
3. Add or update examples when output changes.
4. Run basic checks before submitting:

```bash
python -m compileall reconforge
reconforge --help
```

## Authorized Testing Only

ReconForge is intended only for systems you own or have explicit permission to test. You are responsible for following program scope, laws, terms of service, and rate limits. Do not use ReconForge against unauthorized targets.

## License

MIT. See [`LICENSE`](LICENSE).
