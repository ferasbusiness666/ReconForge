"""Markdown report generation for ReconForge findings."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional

from .github_recon import fetch_github_recon
from .output import ensure_parent
from .portscan import scan_ports
from .scopecheck import evaluate_targets, read_entries
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies


def md_cell(value: object) -> str:
    """Escape a value for a markdown table cell."""
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def build_markdown_report(domain: str, findings: Dict[str, object], scope_notes: Optional[List[str]] = None) -> str:
    """Build a clean markdown report for *domain* from structured *findings*."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subdomains = findings.get("subdomains", []) or []
    port_results = findings.get("ports", {}) or {}
    tech_results = findings.get("technologies", {}) or {}
    github_results = findings.get("github", {}) or {}
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

    lines.extend(["", "## Port Scan Results", ""])
    any_ports = False
    for host, rows in port_results.items():
        if not rows:
            continue
        any_ports = True
        lines.extend([f"### `{host}`", "", "| Port | Status | Banner / Note |", "| --- | --- | --- |"])
        for row in rows:
            note = row.get("banner") or row.get("error") or ""
            lines.append(f"| {md_cell(row.get('port'))} | {md_cell(row.get('status'))} | {md_cell(note)} |")
        lines.append("")
    if not any_ports:
        lines.append("No common port results were collected.")

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
                    lines.append(f"| `{md_cell(key)}` | `{md_cell(value)}` |")
            lines.append("")
    else:
        lines.append("No technology fingerprints were collected.")

    if github_results:
        lines.extend(["", "## GitHub Recon", ""])
        repos = github_results.get("repos", []) or []
        if repos:
            lines.extend(
                [
                    "| Repository | Stars | Forks | Language | Default Branch | Updated | Flags | URL |",
                    "| --- | ---: | ---: | --- | --- | --- | --- | --- |",
                ]
            )
            for repo in repos:
                flags = []
                if repo.get("archived"):
                    flags.append("archived")
                if repo.get("private"):
                    flags.append("private")
                if repo.get("fork"):
                    flags.append("fork")
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            md_cell(repo.get("name")),
                            md_cell(repo.get("stars")),
                            md_cell(repo.get("forks")),
                            md_cell(repo.get("language")),
                            md_cell(repo.get("default_branch")),
                            md_cell(repo.get("updated_at")),
                            md_cell(", ".join(flags) if flags else "-"),
                            md_cell(repo.get("url")),
                        ]
                    )
                    + " |"
                )
            lines.append("")

            for repo in repos:
                lines.extend([f"### `{repo.get('name')}`", ""])
                techs = repo.get("tech_stack", []) or ["No clear metadata"]
                files = repo.get("interesting_files", []) or ["None found"]
                notes = repo.get("recon_notes", []) or ["No specific notes"]
                lines.append(f"- Detected tech stack: {', '.join(f'`{tech}`' for tech in techs)}")
                lines.append(f"- Interesting files: {', '.join(f'`{item}`' for item in files)}")
                lines.append("- Recon notes:")
                lines.extend([f"  - {note}" for note in notes])
                lines.append("")
        else:
            lines.append("No GitHub repositories were collected.")

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
    max_hosts: int = 5,
    github_owner: Optional[str] = None,
    github_repo: Optional[str] = None,
    scope_file: Optional[str] = None,
) -> Dict[str, object]:
    """Run a small recon workflow for *domain* and write a markdown report."""
    subdomains, subdomain_errors = fetch_subdomains(domain, timeout=timeout)
    hosts = subdomains[:max_hosts] if subdomains else [domain]
    port_results = {}
    tech_results = {}
    github_results = {}
    scope_notes: List[str] = []
    errors: List[str] = list(subdomain_errors)

    for host in hosts:
        try:
            scan = scan_ports(host, timeout=2.0)
            port_results[host] = scan.get("results", [])
            errors.extend(scan.get("errors", []))
        except Exception as exc:  # pragma: no cover - defensive report resilience
            port_results[host] = []
            errors.append(f"Port scan failed for {host}: {exc}")

        try:
            tech = detect_technologies(f"https://{host}", timeout=timeout)
            tech_results[f"https://{host}"] = tech
            errors.extend(tech.get("errors", []))
        except Exception as exc:  # pragma: no cover - defensive report resilience
            errors.append(f"Technology detection failed for {host}: {exc}")

    if github_owner:
        try:
            github_results = fetch_github_recon(github_owner, repo=github_repo, timeout=timeout)
            errors.extend(github_results.get("errors", []))
        except Exception as exc:  # pragma: no cover - defensive report resilience
            errors.append(f"GitHub recon failed: {exc}")

    if scope_file:
        scopes, scope_errors = read_entries(scope_file)
        errors.extend(scope_errors)
        if not scope_errors:
            scope_targets = sorted(set([domain, *subdomains]))
            scope_result = evaluate_targets(scope_targets, scopes)
            errors.extend(scope_result.get("errors", []))
            for row in scope_result.get("in_scope", []):
                scope_notes.append(f"{row['target']}: {row['reason']}")
            for row in scope_result.get("out_of_scope", []):
                scope_notes.append(f"{row['target']}: out of scope ({row['reason']})")

    markdown = build_markdown_report(
        domain,
        {
            "subdomains": subdomains,
            "ports": port_results,
            "technologies": tech_results,
            "github": github_results,
            "errors": errors,
        },
        scope_notes=scope_notes,
    )
    output_path = ensure_parent(output)
    output_path.write_text(markdown, encoding="utf-8")
    return {
        "output": output,
        "written": True,
        "hosts": hosts,
        "scope_notes": scope_notes,
        "errors": errors,
    }


def generate_report_from_json(input_path: str, output: str) -> Dict[str, object]:
    """Build a markdown report from a saved JSON findings file."""
    try:
        findings = json.loads(Path(input_path).read_text(encoding="utf-8"))
    except OSError as exc:
        return {
            "output": output,
            "written": False,
            "hard_failure": True,
            "errors": [f"Could not read {input_path}: {exc}"],
        }
    except ValueError as exc:
        return {
            "output": output,
            "written": False,
            "hard_failure": True,
            "errors": [f"Invalid JSON in {input_path}: {exc}"],
        }

    if not isinstance(findings, dict):
        return {
            "output": output,
            "written": False,
            "hard_failure": True,
            "errors": [f"Invalid findings structure in {input_path}."],
        }

    domain = str(findings.get("domain") or findings.get("target") or "saved-recon")
    scope_notes = findings.get("scope_notes", []) if isinstance(findings.get("scope_notes", []), list) else []
    markdown = build_markdown_report(domain, findings, scope_notes=scope_notes)
    output_path = ensure_parent(output)
    output_path.write_text(markdown, encoding="utf-8")
    return {
        "output": output,
        "written": True,
        "hard_failure": False,
        "hosts": list((findings.get("ports") or {}).keys()),
        "scope_notes": scope_notes,
        "errors": findings.get("errors", []) or [],
    }
