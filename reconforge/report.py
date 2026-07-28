"""Markdown report generation for ReconForge findings."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .github_recon import fetch_github_recon
from .output import ensure_parent
from .portscan import scan_ports
from .scopecheck import evaluate_targets, read_entries
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies


def md_cell(value: object) -> str:
    """Escape a value for a markdown table cell."""
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _append_unique(target: List[object], values: Iterable[object]) -> None:
    """Append values while preserving order and avoiding duplicates."""
    for value in values:
        if value not in target:
            target.append(value)


def _merge_github(target: Dict[str, object], source: Dict[str, object]) -> None:
    """Merge normalized GitHub recon payloads without duplicating repositories."""
    if not target:
        target.update({"owner": "", "repo": None, "repos": [], "errors": [], "rate_limit": {}})
    if source.get("owner") and not target.get("owner"):
        target["owner"] = source.get("owner")
    if source.get("repo") and not target.get("repo"):
        target["repo"] = source.get("repo")

    repos = target.setdefault("repos", [])
    if isinstance(repos, list) and isinstance(source.get("repos"), list):
        _append_unique(repos, source["repos"])
    github_errors = target.setdefault("errors", [])
    if isinstance(github_errors, list) and isinstance(source.get("errors"), list):
        _append_unique(github_errors, source["errors"])
    if isinstance(source.get("rate_limit"), dict):
        target["rate_limit"] = source["rate_limit"]


def merge_saved_findings(
    payloads: List[Tuple[str, Dict[str, object]]],
) -> Tuple[str, Dict[str, object], List[str]]:
    """Merge full findings and command-specific JSON payloads for reporting."""
    merged: Dict[str, object] = {
        "subdomains": [],
        "ports": {},
        "technologies": {},
        "http_probes": [],
        "github": {},
        "errors": [],
    }
    scope_notes: List[str] = []
    domains: List[str] = []
    multiple_sources = len(payloads) > 1

    for source_path, payload in payloads:
        command = str(payload.get("command") or "")
        source_name = Path(source_path).name
        for key in ("domain", "target", "host"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip() and value not in domains:
                domains.append(value.strip())
                break

        errors = payload.get("errors")
        if isinstance(errors, list):
            normalized = [
                f"{source_name}: {error}" if multiple_sources else str(error)
                for error in errors
            ]
            _append_unique(merged["errors"], normalized)  # type: ignore[arg-type]

        subdomains = payload.get("subdomains")
        if isinstance(subdomains, list):
            _append_unique(merged["subdomains"], subdomains)  # type: ignore[arg-type]

        ports = payload.get("ports")
        if isinstance(ports, dict):
            merged_ports = merged["ports"]
            if isinstance(merged_ports, dict):
                for host, rows in ports.items():
                    if not isinstance(rows, list):
                        continue
                    target_rows = merged_ports.setdefault(str(host), [])
                    if isinstance(target_rows, list):
                        _append_unique(target_rows, rows)
        elif command == "portscan" and isinstance(payload.get("results"), list):
            host = str(payload.get("host") or payload.get("target") or "saved-target")
            merged_ports = merged["ports"]
            if isinstance(merged_ports, dict):
                target_rows = merged_ports.setdefault(host, [])
                if isinstance(target_rows, list):
                    _append_unique(target_rows, payload["results"])

        technologies = payload.get("technologies")
        if isinstance(technologies, dict):
            merged_tech = merged["technologies"]
            if isinstance(merged_tech, dict):
                merged_tech.update(technologies)
        elif command == "techdetect":
            url = str(payload.get("url") or "saved-url")
            merged_tech = merged["technologies"]
            if isinstance(merged_tech, dict):
                merged_tech[url] = {
                    key: value
                    for key, value in payload.items()
                    if key not in {"command", "schema_version"}
                }

        http_probes = payload.get("http_probes")
        if isinstance(http_probes, list):
            _append_unique(merged["http_probes"], http_probes)  # type: ignore[arg-type]
        elif command == "httpprobe" and isinstance(payload.get("results"), list):
            _append_unique(merged["http_probes"], payload["results"])  # type: ignore[arg-type]

        github_data = payload.get("github")
        if isinstance(github_data, dict):
            _merge_github(merged["github"], github_data)  # type: ignore[arg-type]
            nested_errors = github_data.get("errors")
            if isinstance(nested_errors, list):
                _append_unique(merged["errors"], nested_errors)  # type: ignore[arg-type]
        elif command == "github":
            _merge_github(merged["github"], payload)  # type: ignore[arg-type]

        saved_scope = payload.get("scope_notes")
        if isinstance(saved_scope, list):
            _append_unique(scope_notes, [str(note) for note in saved_scope])
        if command == "scopecheck":
            in_scope = payload.get("in_scope")
            if isinstance(in_scope, list):
                _append_unique(
                    scope_notes,
                    [
                        f"{row.get('target')}: {row.get('reason')}"
                        for row in in_scope
                        if isinstance(row, dict)
                    ],
                )
            out_of_scope = payload.get("out_of_scope")
            if isinstance(out_of_scope, list):
                _append_unique(
                    scope_notes,
                    [
                        f"{row.get('target')}: out of scope ({row.get('reason')})"
                        for row in out_of_scope
                        if isinstance(row, dict)
                    ],
                )

    domain = domains[0] if domains else "saved-recon"
    if len(domains) > 1:
        merged_errors = merged["errors"]
        if isinstance(merged_errors, list):
            merged_errors.append(
                f"Merged inputs reference multiple targets; report title uses {domain}: {', '.join(domains)}"
            )
    return domain, merged, scope_notes


def build_markdown_report(domain: str, findings: Dict[str, object], scope_notes: Optional[List[str]] = None) -> str:
    """Build a clean markdown report for *domain* from structured *findings*."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subdomains = findings.get("subdomains", []) or []
    port_results = findings.get("ports", {}) or {}
    tech_results = findings.get("technologies", {}) or {}
    http_results = findings.get("http_probes", []) or []
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
        f"- HTTP probes collected: **{sum(len(item.get('probes', [])) for item in http_results if isinstance(item, dict))}**",
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

    lines.extend(["", "## HTTP Probe Results", ""])
    probe_rows = []
    for item in http_results:
        if not isinstance(item, dict):
            continue
        host = item.get("host") or ""
        for probe in item.get("probes", []) or []:
            if isinstance(probe, dict):
                probe_rows.append((host, probe))
    if probe_rows:
        lines.extend(
            [
                "| Host | Status | Length | Server | Technologies | Title | Final URL |",
                "| --- | ---: | ---: | --- | --- | --- | --- |",
            ]
        )
        for host, probe in probe_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_cell(host),
                        md_cell(probe.get("status_code")),
                        md_cell(probe.get("content_length")),
                        md_cell(probe.get("server")),
                        md_cell(", ".join(probe.get("technologies", []) or [])),
                        md_cell(probe.get("title")),
                        md_cell(probe.get("final_url") or probe.get("url")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("No HTTP probe results were provided.")

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
        "hard_failure": False,
        "hosts": hosts,
        "scope_notes": scope_notes,
        "errors": errors,
    }


def generate_report_from_json(
    input_paths: Union[str, Iterable[str]],
    output: str,
) -> Dict[str, object]:
    """Build a markdown report from one or more saved JSON findings files."""
    paths = [input_paths] if isinstance(input_paths, str) else list(input_paths)
    if not paths:
        return {
            "output": output,
            "written": False,
            "hard_failure": True,
            "errors": ["At least one JSON findings file is required."],
        }

    payloads: List[Tuple[str, Dict[str, object]]] = []
    input_errors: List[str] = []
    for input_path in paths:
        try:
            findings = json.loads(Path(input_path).read_text(encoding="utf-8"))
        except OSError as exc:
            input_errors.append(f"Could not read {input_path}: {exc}")
            continue
        except ValueError as exc:
            input_errors.append(f"Invalid JSON in {input_path}: {exc}")
            continue

        if not isinstance(findings, dict):
            input_errors.append(f"Invalid findings structure in {input_path}.")
            continue
        payloads.append((input_path, findings))

    if input_errors:
        return {
            "output": output,
            "written": False,
            "hard_failure": True,
            "errors": input_errors,
        }

    domain, findings, scope_notes = merge_saved_findings(payloads)
    markdown = build_markdown_report(domain, findings, scope_notes=scope_notes)
    output_path = ensure_parent(output)
    output_path.write_text(markdown, encoding="utf-8")
    return {
        "output": output,
        "written": True,
        "hard_failure": False,
        "sources": paths,
        "hosts": list((findings.get("ports") or {}).keys()),
        "scope_notes": scope_notes,
        "errors": findings.get("errors", []) or [],
    }
