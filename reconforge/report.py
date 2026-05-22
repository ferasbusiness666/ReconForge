"""Markdown report generation for ReconForge findings."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .portscan import scan_ports
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies


def build_markdown_report(domain: str, findings: Dict[str, object], scope_notes: Optional[List[str]] = None) -> str:
    """Build a clean markdown report for *domain* from structured *findings*."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subdomains = findings.get("subdomains", []) or []
    port_results = findings.get("ports", {}) or {}
    tech_results = findings.get("technologies", {}) or {}
    errors = findings.get("errors", []) or []

    lines = [
        f"# ReconForge Report: {domain}",
        "",
        f"**Generated:** {timestamp}",
        f"**Target domain:** `{domain}`",
        "",
        "## Summary",
        "",
        f"- Subdomains found: **{len(subdomains)}**",
        f"- Hosts scanned for ports: **{len(port_results)}**",
        f"- Technology fingerprints collected: **{len(tech_results)}**",
        "",
        "## Subdomains Found",
        "",
    ]

    if subdomains:
        lines.extend([f"- `{item}`" for item in subdomains])
    else:
        lines.append("No subdomains were discovered.")

    lines.extend(["", "## Open Ports and Banners", ""])
    any_open = False
    for host, rows in port_results.items():
        open_rows = [row for row in rows if row.get("status") == "open"]
        if not open_rows:
            continue
        any_open = True
        lines.extend([f"### `{host}`", "", "| Port | Status | Banner |", "| --- | --- | --- |"])
        for row in open_rows:
            banner = str(row.get("banner") or "").replace("|", "\\|")
            port = row.get('port')
            status = row.get('status')
            lines.append(f"| {port} | {status} | {banner} |")
        lines.append("")
    if not any_open:
        lines.append("No open common ports were identified.")

    lines.extend(["", "## Detected Technologies", ""])
    if tech_results:
        for url, result in tech_results.items():
            techs = result.get("technologies", []) or ["No clear fingerprints"]
            lines.extend([f"### `{url}`", "", f"- HTTP status: `{result.get('status_code')}`"])
            lines.append(f"- Technologies: {', '.join(f'`{tech}`' for tech in techs)}")
            headers = result.get("headers", {}) or {}
            if headers:
                lines.extend(["", "| Header | Value |", "| --- | --- |"])
                for key, value in headers.items():
                    escaped_value = str(value).replace('|', '\\|')
                    lines.append(f"| `{key}` | `{escaped_value}` |")
            lines.append("")
    else:
        lines.append("No technology fingerprints were collected.")

    lines.extend(["", "## Scope Notes", ""])
    if scope_notes:
        lines.extend([f"- {note}" for note in scope_notes])
    else:
        lines.append("No scope notes were provided.")

    if errors:
        lines.extend(["", "## Collection Notes", ""])
        lines.extend([f"- {error}" for error in errors])

    lines.append("")
    return "\n".join(lines)


def generate_report(
    domain: str,
    output: str,
    timeout: float = 10.0,
    max_hosts: Optional[int] = None,
    concurrent: bool = True,
) -> Dict[str, object]:
    """Run a recon workflow for *domain* and write a markdown report.
    
    Args:
        domain: Target domain to scan
        output: Output file path for markdown report
        timeout: Request timeout in seconds
        max_hosts: Maximum hosts to scan (None = all discovered)
        concurrent: Use concurrent port scanning for speed
    
    Returns:
        Dictionary with output path, scanned hosts, and errors
    """
    subdomains, subdomain_errors = fetch_subdomains(domain, timeout=timeout)
    hosts = subdomains[:max_hosts] if max_hosts and subdomains else (subdomains or [domain])
    port_results = {}
    tech_results = {}
    errors: List[str] = list(subdomain_errors)

    for host in hosts:
        # Use concurrent scanning for faster results
        scan = scan_ports(host, timeout=2.0, concurrent=concurrent, max_workers=4)
        port_results[host] = scan.get("results", [])
        errors.extend(scan.get("errors", []))

        # Try both HTTPS and HTTP if HTTPS fails
        for protocol in ["https", "http"]:
            url = f"{protocol}://{host}"
            tech = detect_technologies(url, timeout=timeout)
            if tech.get("status_code") or not tech.get("errors"):
                tech_results[url] = tech
                errors.extend(tech.get("errors", []))
                break
            errors.extend(tech.get("errors", []))

    markdown = build_markdown_report(
        domain,
        {"subdomains": subdomains, "ports": port_results, "technologies": tech_results, "errors": errors},
    )
    Path(output).write_text(markdown, encoding="utf-8")
    return {"output": output, "hosts": hosts, "errors": errors}
