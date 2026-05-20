"""Command-line interface for the ReconForge toolkit."""

from __future__ import annotations

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .portscan import scan_ports
from .report import generate_report
from .scopecheck import check_targets
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies

console = Console()


def print_errors(errors: list[str]) -> None:
    """Print clear user-facing error messages with Rich styling."""
    for error in errors:
        console.print(f"[bold red]Error:[/bold red] {error}")


@click.group()
def cli() -> None:
    """AI-assisted recon toolkit for bug bounty hunters."""


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to enumerate, e.g. example.com")
def subdomains(domain: str) -> None:
    """Discover subdomains for a domain using crt.sh."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Querying crt.sh for {domain}...", total=None)
        results, errors = fetch_subdomains(domain)

    print_errors(errors)
    table = Table(title=f"Subdomains for {domain}")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Subdomain", style="green")
    for index, name in enumerate(results, start=1):
        table.add_row(str(index), name)
    console.print(table)
    console.print(f"[bold]Total:[/bold] {len(results)}")


@cli.command()
@click.option("-t", "--target", required=True, help="Host to scan, e.g. sub.example.com")
def portscan(target: str) -> None:
    """Scan common TCP ports for a target host."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Scanning common ports on {target}...", total=None)
        scan = scan_ports(target)

    print_errors(scan.get("errors", []))
    table = Table(title=f"Port scan for {target}")
    table.add_column("Port", justify="right", style="cyan")
    table.add_column("Status")
    table.add_column("Banner / Note", overflow="fold")
    for row in scan.get("results", []):
        status = row.get("status")
        style = "bold green" if status == "open" else "dim red"
        indicator = "🟢 open" if status == "open" else "🔴 closed"
        if status == "error":
            style = "bold red"
            indicator = "⚠ error"
        note = row.get("banner") or row.get("error") or ""
        table.add_row(str(row.get("port")), f"[{style}]{indicator}[/{style}]", str(note))
    console.print(table)


@cli.command()
@click.option("-u", "--url", required=True, help="URL to fingerprint, e.g. https://sub.example.com")
def techdetect(url: str) -> None:
    """Detect HTTP technologies from headers and lightweight body signals."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Fingerprinting {url}...", total=None)
        result = detect_technologies(url)

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


@cli.command()
@click.option("-t", "--targets", required=True, type=click.Path(exists=True, dir_okay=False), help="File containing targets")
@click.option("-s", "--scope", required=True, type=click.Path(exists=True, dir_okay=False), help="File containing scope rules")
def scopecheck(targets: str, scope: str) -> None:
    """Separate targets into in-scope and out-of-scope groups."""
    result = check_targets(targets, scope)
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


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to report on, e.g. example.com")
@click.option("--output", required=True, type=click.Path(dir_okay=False), help="Markdown report output path")
def report(domain: str, output: str) -> None:
    """Generate a markdown recon report for a domain."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Generating report for {domain}...", total=None)
        result = generate_report(domain, output)
    print_errors(result.get("errors", []))
    console.print(f"[bold green]Report written:[/bold green] {output}")


if __name__ == "__main__":
    cli()
