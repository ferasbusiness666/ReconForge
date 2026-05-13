"""Command-line interface for the ReconForge toolkit."""

from __future__ import annotations

import json
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import config_section, load_config
from .github_recon import fetch_github_recon
from .httpprobe import probe_hosts_file
from .output import write_json, write_lines, write_text
from .portscan import resolve_ports, scan_ports
from .report import generate_report, generate_report_from_json
from .scopecheck import check_targets
from .summarize import summarize_report
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies

console = Console()


def print_errors(errors: list[str]) -> None:
    """Print clear user-facing error messages with Rich styling."""
    for error in errors:
        console.print(f"[bold red]Error:[/bold red] {error}")


def print_status(message: str) -> None:
    """Print a plain ASCII status line that is safe in Windows consoles."""
    console.print(f"[dim]{message}[/dim]")


def print_json(data: object) -> None:
    """Print a stable JSON payload for automation."""
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@click.group()
def cli() -> None:
    """AI-assisted recon toolkit for authorized bug bounty testing."""


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to enumerate, e.g. example.com")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def subdomains(domain: str, output: Optional[str], json_output: bool) -> None:
    """Discover subdomains for a domain using public sources."""
    if not json_output:
        print_status(f"Querying public subdomain sources for {domain}...")
    results, errors = fetch_subdomains(domain)
    payload = {"domain": domain, "subdomains": results, "errors": errors}

    if json_output:
        if output:
            write_json(output, payload)
        print_json(payload)
        return

    if output:
        write_lines(output, results)
    print_errors(errors)
    table = Table(title=f"Subdomains for {domain}")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Subdomain", style="green")
    for index, name in enumerate(results, start=1):
        table.add_row(str(index), name)
    console.print(table)
    console.print(f"[bold]Total:[/bold] {len(results)}")
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-t", "--target", required=True, help="Host to scan, e.g. sub.example.com")
@click.option("--profile", type=click.Choice(["safe", "normal", "deep"]), help="Port scan profile")
@click.option("--ports", help="Comma-separated custom ports; overrides --profile")
@click.option("--timeout", type=float, help="TCP connect timeout in seconds")
@click.option("--config", "config_path", default="reconforge.json", show_default=True, help="Optional JSON config file")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def portscan(target: str, profile: Optional[str], ports: Optional[str], timeout: Optional[float], config_path: str, output: Optional[str], json_output: bool) -> None:
    """Scan common TCP ports for a target host."""
    config, config_errors = load_config(config_path)
    portscan_config = config_section(config, "portscan")
    resolved_profile = profile or str(portscan_config.get("profile") or "safe")
    config_ports = portscan_config.get("ports")
    ports_text = ports
    if ports_text is None and config_ports:
        ports_text = ",".join(str(port) for port in config_ports) if isinstance(config_ports, list) else str(config_ports)
    resolved_timeout = timeout if timeout is not None else float(portscan_config.get("timeout") or 2.0)

    if not json_output:
        print_status(f"Scanning common ports on {target}...")
    try:
        resolved_ports = resolve_ports(profile=resolved_profile, ports_text=ports_text)
    except ValueError as exc:
        raise click.BadParameter(str(exc), param_hint="--ports") from exc
    scan = scan_ports(target, ports=resolved_ports, timeout=resolved_timeout, profile=resolved_profile)
    scan["profile"] = resolved_profile
    scan["errors"] = config_errors + list(scan.get("errors", []))

    if json_output:
        if output:
            write_json(output, scan)
        print_json(scan)
        return

    if output:
        write_json(output, scan)
    print_errors(scan.get("errors", []))
    table = Table(title=f"Port scan for {target}")
    table.add_column("Port", justify="right", style="cyan")
    table.add_column("Status")
    table.add_column("Banner / Note", overflow="fold")
    for row in scan.get("results", []):
        status = str(row.get("status") or "")
        style = "bold green" if status == "open" else "dim"
        if status == "closed":
            style = "dim red"
        elif status == "filtered/timeout":
            style = "yellow"
        elif status == "error":
            style = "bold red"
        note = row.get("banner") or row.get("error") or ""
        table.add_row(str(row.get("port")), f"[{style}]{status}[/{style}]", str(note))
    console.print(table)
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-u", "--url", required=True, help="URL to fingerprint, e.g. https://sub.example.com")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def techdetect(url: str, output: Optional[str], json_output: bool) -> None:
    """Detect HTTP technologies from headers and lightweight body signals."""
    if not json_output:
        print_status(f"Fingerprinting {url}...")
    result = detect_technologies(url)

    if json_output:
        if output:
            write_json(output, result)
        print_json(result)
        return

    if output:
        write_json(output, result)
    print_errors(result.get("errors", []))
    console.print(f"[bold]Final URL:[/bold] {result.get('url')}")
    console.print(f"[bold]HTTP status:[/bold] {result.get('status_code')}")

    tech_table = Table(title="Detected Technologies")
    tech_table.add_column("Technology", style="green")
    for tech in result.get("technologies", []):
        tech_table.add_row(tech)
    if not result.get("technologies"):
        tech_table.add_row("No clear fingerprints")
    console.print(tech_table)

    header_table = Table(title="Interesting Headers")
    header_table.add_column("Header", style="cyan")
    header_table.add_column("Value", overflow="fold")
    for key, value in result.get("headers", {}).items():
        header_table.add_row(key, value)
    if not result.get("headers"):
        header_table.add_row("None", "No interesting headers observed")
    console.print(header_table)
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-o", "--owner", required=True, help="GitHub owner or organization, e.g. microsoft")
@click.option("-r", "--repo", help="Optional repository name, e.g. vscode")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def github(owner: str, repo: Optional[str] = None, output: Optional[str] = None, json_output: bool = False) -> None:
    """Collect lightweight GitHub repository recon from the public API."""
    label = f"{owner}/{repo}" if repo else owner
    if not json_output:
        print_status(f"Querying GitHub for {label}...")
    result = fetch_github_recon(owner, repo=repo)

    if json_output:
        if output:
            write_json(output, result)
        print_json(result)
        return

    if output:
        write_json(output, result)
    print_errors(result.get("errors", []))
    repos = result.get("repos", []) or []

    summary = Table(title=f"GitHub Recon for {label}")
    summary.add_column("Repository", style="green")
    summary.add_column("Stars", justify="right")
    summary.add_column("Forks", justify="right")
    summary.add_column("Language")
    summary.add_column("Default")
    summary.add_column("Updated")
    summary.add_column("Flags")
    summary.add_column("URL", overflow="fold")
    for item in repos:
        flags = []
        if item.get("archived"):
            flags.append("archived")
        if item.get("private"):
            flags.append("private")
        if item.get("fork"):
            flags.append("fork")
        summary.add_row(
            str(item.get("name") or ""),
            str(item.get("stars") or 0),
            str(item.get("forks") or 0),
            str(item.get("language") or ""),
            str(item.get("default_branch") or ""),
            str(item.get("updated_at") or ""),
            ", ".join(flags) if flags else "-",
            str(item.get("url") or ""),
        )
    if not repos:
        summary.add_row("None", "0", "0", "", "", "", "", "No repositories collected")
    console.print(summary)

    details = Table(title="Detected Tech, Files, and Recon Notes")
    details.add_column("Repository", style="green")
    details.add_column("Tech Stack", overflow="fold")
    details.add_column("Interesting Files", overflow="fold")
    details.add_column("Recon Notes", overflow="fold")
    for item in repos:
        details.add_row(
            str(item.get("name") or ""),
            ", ".join(item.get("tech_stack", []) or ["No clear metadata"]),
            ", ".join(item.get("interesting_files", []) or ["None found"]),
            "; ".join(item.get("recon_notes", []) or ["No specific notes"]),
        )
    if not repos:
        details.add_row("None", "-", "-", "-")
    console.print(details)
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-i", "--input", "input_file", required=True, type=click.Path(exists=True, dir_okay=False), help="File containing hosts or URLs")
@click.option("--timeout", default=5.0, show_default=True, help="Request timeout in seconds")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def httpprobe(input_file: str, timeout: float, output: Optional[str], json_output: bool) -> None:
    """Probe HTTP and HTTPS reachability for hosts from a file."""
    if not json_output:
        print_status(f"Probing HTTP/HTTPS targets from {input_file}...")
    result = probe_hosts_file(input_file, timeout=timeout)

    if json_output:
        if output:
            write_json(output, result)
        print_json(result)
        return

    if output:
        write_json(output, result)
    print_errors(result.get("errors", []))
    table = Table(title=f"HTTP Probe Results for {input_file}")
    table.add_column("Host", style="green")
    table.add_column("URL", overflow="fold")
    table.add_column("Status", justify="right")
    table.add_column("Title", overflow="fold")
    table.add_column("Error", overflow="fold")
    for item in result.get("results", []):
        host = str(item.get("host") or "")
        for probe in item.get("probes", []):
            table.add_row(
                host,
                str(probe.get("final_url") or probe.get("url") or ""),
                str(probe.get("status_code") or ""),
                str(probe.get("title") or ""),
                str(probe.get("error") or ""),
            )
    if not result.get("results"):
        table.add_row("None", "", "", "", "No targets probed")
    console.print(table)
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-t", "--targets", required=True, type=click.Path(exists=True, dir_okay=False), help="File containing targets")
@click.option("-s", "--scope", required=True, type=click.Path(exists=True, dir_okay=False), help="File containing scope rules")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional JSON output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def scopecheck(targets: str, scope: str, output: Optional[str], json_output: bool) -> None:
    """Separate targets into in-scope and out-of-scope groups."""
    result = check_targets(targets, scope)

    if json_output:
        if output:
            write_json(output, result)
        print_json(result)
        return

    if output:
        write_json(output, result)
    print_errors(result.get("errors", []))

    in_table = Table(title="In-Scope Targets")
    in_table.add_column("Target", style="green")
    in_table.add_column("Reason")
    for row in result.get("in_scope", []):
        in_table.add_row(row["target"], row["reason"])
    if not result.get("in_scope"):
        in_table.add_row("None", "No targets matched scope")
    console.print(in_table)

    out_table = Table(title="Out-of-Scope Targets")
    out_table.add_column("Target", style="red")
    out_table.add_column("Reason")
    for row in result.get("out_of_scope", []):
        out_table.add_row(row["target"], row["reason"])
    if not result.get("out_of_scope"):
        out_table.add_row("None", "All targets matched scope")
    console.print(out_table)
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


@cli.command()
@click.option("-d", "--domain", help="Domain to report on, e.g. example.com")
@click.option("--github-owner", help="Optional GitHub owner or organization to include in the report")
@click.option("--github-repo", help="Optional GitHub repository to include in the report")
@click.option("--scope", "scope_file", type=click.Path(exists=True, dir_okay=False), help="Optional scope file for report scope notes")
@click.option("--from-json", "from_json", type=click.Path(exists=True, dir_okay=False), help="Build report from saved JSON findings")
@click.option("--output", required=True, type=click.Path(dir_okay=False), help="Markdown report output path")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON summary")
def report(
    domain: Optional[str],
    github_owner: Optional[str],
    github_repo: Optional[str],
    scope_file: Optional[str],
    from_json: Optional[str],
    output: str,
    json_output: bool,
) -> None:
    """Generate a markdown recon report for a domain."""
    if not json_output:
        print_status(f"Generating report for {domain or from_json}...")
    if from_json:
        result = generate_report_from_json(from_json, output)
    else:
        if not domain:
            raise click.ClickException("Either --domain or --from-json is required.")
        result = generate_report(domain, output, github_owner=github_owner, github_repo=github_repo, scope_file=scope_file)

    if json_output:
        print_json(result)
        return

    print_errors(result.get("errors", []))
    console.print(f"[bold green]Report written:[/bold green] {output}")


@cli.command()
@click.option("--report", "report_path", required=True, type=click.Path(exists=True, dir_okay=False), help="Markdown report to summarize")
@click.option("--output", type=click.Path(dir_okay=False), help="Optional text output file")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON output")
def summarize(report_path: str, output: Optional[str], json_output: bool) -> None:
    """Create an AI-ready summary from a markdown report without calling an AI API."""
    result = summarize_report(report_path)
    if output:
        if json_output:
            write_json(output, result)
        else:
            write_text(output, str(result.get("summary") or ""))

    if json_output:
        print_json(result)
        return

    print_errors(result.get("errors", []))
    console.print(str(result.get("summary") or ""))
    if output:
        console.print(f"[bold green]Output written:[/bold green] {output}")


if __name__ == "__main__":
    cli()
