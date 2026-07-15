"""Enhanced command-line interface for the ReconForge toolkit."""

from __future__ import annotations

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .cache import get_cache
from .config import get_config
from .export import (
    export_csv_ports,
    export_csv_subdomains,
    export_csv_technologies,
    export_html_report,
    export_json,
)
from .portscan import scan_ports
from .report import generate_report
from .scopecheck import check_targets
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies
from .dns_enum import (
    enumerate_dns_records,
    brute_force_subdomains,
    reverse_dns_lookup,
    get_mx_records,
    get_ns_records,
)

console = Console()


def print_errors(errors: list[str]) -> None:
    """Print clear user-facing error messages with Rich styling."""
    for error in errors:
        console.print(f"[bold red]Error:[/bold red] {error}")


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """🔍 ReconForge - AI-assisted recon toolkit for bug bounty hunters."""


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to enumerate, e.g. example.com")
@click.option("--cache/--no-cache", default=True, help="Use cached results if available")
def subdomains(domain: str, cache: bool) -> None:
    """Discover subdomains for a domain using crt.sh."""
    cache_obj = get_cache() if cache else None
    cache_key = f"subdomains:{domain}"

    # Check cache first
    if cache_obj:
        cached = cache_obj.get(cache_key)
        if cached:
            console.print("[yellow]📦 Using cached results[/yellow]")
            results = cached.get("subdomains", [])
            errors = cached.get("errors", [])
        else:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(f"Querying crt.sh for {domain}...", total=None)
                results, errors = fetch_subdomains(domain)
            if cache_obj:
                cache_obj.set(cache_key, {"subdomains": results, "errors": errors})
    else:
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
@click.option("--concurrent/--sequential", default=True, help="Use concurrent scanning")
@click.option("--timeout", default=2.0, help="Socket timeout in seconds")
def portscan(target: str, concurrent: bool, timeout: float) -> None:
    """Scan common TCP ports for a target host."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Scanning common ports on {target}...", total=None)
        scan = scan_ports(target, timeout=timeout, concurrent=concurrent)

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
@click.option("--timeout", default=10.0, help="Request timeout in seconds")
def techdetect(url: str, timeout: float) -> None:
    """Detect HTTP technologies from headers and lightweight body signals."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Fingerprinting {url}...", total=None)
        result = detect_technologies(url, timeout=timeout)

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
@click.option("--format", type=click.Choice(["md", "json", "html"]), default="md", help="Output format")
@click.option("--max-hosts", type=int, default=None, help="Maximum hosts to scan")
@click.option("--concurrent/--sequential", default=True, help="Use concurrent scanning")
def report(domain: str, output: str, format: str, max_hosts: int, concurrent: bool) -> None:
    """Generate a comprehensive recon report for a domain."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task(f"Generating report for {domain}...", total=None)
        result = generate_report(domain, output, max_hosts=max_hosts, concurrent=concurrent)

    print_errors(result.get("errors", []))

    # Export in additional formats if requested
    if format != "md":
        # Read the markdown report to get findings
        from pathlib import Path
        from .report import build_markdown_report

        subdomains, _ = fetch_subdomains(domain)
        hosts = subdomains[:max_hosts] if max_hosts and subdomains else (subdomains or [domain])
        port_results = {}
        tech_results = {}
        errors = []

        for host in hosts:
            scan = scan_ports(host, timeout=2.0, concurrent=concurrent)
            port_results[host] = scan.get("results", [])
            errors.extend(scan.get("errors", []))

            for protocol in ["https", "http"]:
                url = f"{protocol}://{host}"
                tech = detect_technologies(url, timeout=10.0)
                if tech.get("status_code") or not tech.get("errors"):
                    tech_results[url] = tech
                    break

        findings = {
            "subdomains": subdomains,
            "ports": port_results,
            "technologies": tech_results,
            "errors": errors,
        }

        if format == "json":
            json_output = output.replace(".md", ".json")
            export_json(findings, json_output)
            console.print(f"[bold green]JSON report written:[/bold green] {json_output}")

        elif format == "html":
            html_output = output.replace(".md", ".html")
            export_html_report(domain, findings, html_output)
            console.print(f"[bold green]HTML report written:[/bold green] {html_output}")

    console.print(f"[bold green]Report written:[/bold green] {output}")


@cli.command()
def cache_stats() -> None:
    """Show cache statistics."""
    cache = get_cache()
    stats = cache.get_stats()

    table = Table(title="Cache Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total Entries", str(stats["total_entries"]))
    table.add_row("Cache Size", f"{stats['cache_size_bytes']} bytes")
    table.add_row("Cache Path", stats["cache_path"])
    console.print(table)


@cli.command()
def cache_clear() -> None:
    """Clear all cached results."""
    cache = get_cache()
    cache.clear()
    console.print("[bold green]✓[/bold green] Cache cleared")


@cli.command()
def config_show() -> None:
    """Show current configuration."""
    config = get_config()

    table = Table(title="ReconForge Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    for key, value in config.config.items():
        table.add_row(key, str(value))
    console.print(table)


@cli.command()
@click.option("--key", required=True, help="Configuration key")
@click.option("--value", required=True, help="Configuration value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    config = get_config()
    
    # Try to parse as appropriate type
    try:
        if value.lower() in ("true", "false"):
            config.set(key, value.lower() == "true")
        elif value.isdigit():
            config.set(key, int(value))
        elif value.replace(".", "", 1).isdigit():
            config.set(key, float(value))
        else:
            config.set(key, value)
    except Exception:
        config.set(key, value)
    
    config.save()
    console.print(f"[bold green]✓[/bold green] Set {key} = {config.get(key)}")


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to enumerate DNS records")
@click.option("-t", "--type", default="all", help="Record type: A, AAAA, MX, NS, TXT, CNAME, SOA, SRV, or 'all'")
def dns_enum(domain: str, type: str) -> None:
    """Enumerate DNS records for a domain."""
    console.print(f"[bold cyan]🔍 DNS Enumeration for {domain}[/bold cyan]")
    
    if type.upper() == "ALL":
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Enumerating DNS records...", total=None)
            result = enumerate_dns_records(domain)
        
        if result["records"]:
            for record_type, records in result["records"].items():
                console.print(f"\n[bold yellow]{record_type} Records:[/bold yellow]")
                for record in records:
                    console.print(f"  • {record}")
        
        if result["errors"]:
            print_errors(result["errors"])
    else:
        result = enumerate_dns_records(domain)
        records = result["records"].get(type.upper(), [])
        if records:
            console.print(f"\n[bold yellow]{type.upper()} Records:[/bold yellow]")
            for record in records:
                console.print(f"  • {record}")
        else:
            console.print(f"[bold red]✗[/bold red] No {type.upper()} records found")


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to brute force subdomains")
@click.option("-w", "--wordlist", default=None, help="Path to wordlist file (optional)")
@click.option("-t", "--threads", default=10, help="Number of concurrent threads")
def dns_brute(domain: str, wordlist: str | None, threads: int) -> None:
    """Brute force DNS subdomains."""
    console.print(f"[bold cyan]🔍 DNS Brute Force for {domain}[/bold cyan]")
    
    wordlist_data = None
    if wordlist:
        try:
            with open(wordlist, "r") as f:
                wordlist_data = [line.strip() for line in f if line.strip()]
                console.print(f"[bold green]✓[/bold green] Loaded {len(wordlist_data)} subdomains from {wordlist}")
        except FileNotFoundError:
            console.print(f"[bold red]✗[/bold red] Wordlist file not found: {wordlist}")
            return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Brute forcing subdomains...", total=None)
        result = brute_force_subdomains(domain, wordlist_data, max_workers=threads)
    
    if result["subdomains"]:
        console.print(f"\n[bold green]✓ Found {result['count']} subdomains:[/bold green]")
        table = Table(title=f"Discovered Subdomains for {domain}")
        table.add_column("#", style="cyan")
        table.add_column("Subdomain", style="green")
        for idx, subdomain in enumerate(result["subdomains"], 1):
            table.add_row(str(idx), subdomain)
        console.print(table)
    else:
        console.print("[bold yellow]⚠ No subdomains found[/bold yellow]")
    
    if result["errors"]:
        print_errors(result["errors"])


@cli.command()
@click.option("-i", "--ip", required=True, help="IP address to reverse lookup")
def dns_reverse(ip: str) -> None:
    """Perform reverse DNS lookup on an IP address."""
    console.print(f"[bold cyan]🔍 Reverse DNS Lookup for {ip}[/bold cyan]")
    
    result = reverse_dns_lookup(ip)
    if result["hostname"]:
        console.print(f"[bold green]✓ Hostname:[/bold green] {result['hostname']}")
    else:
        if result["errors"]:
            print_errors(result["errors"])
        else:
            console.print("[bold yellow]⚠ No hostname found[/bold yellow]")


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to query MX records")
def dns_mx(domain: str) -> None:
    """Get MX records for a domain."""
    console.print(f"[bold cyan]📧 MX Records for {domain}[/bold cyan]")
    
    result = get_mx_records(domain)
    if result["mx_records"]:
        table = Table(title=f"MX Records for {domain}")
        table.add_column("Preference", style="cyan")
        table.add_column("Exchange", style="green")
        for mx in result["mx_records"]:
            table.add_row(str(mx["preference"]), mx["exchange"])
        console.print(table)
    else:
        if result["errors"]:
            print_errors(result["errors"])
        else:
            console.print("[bold yellow]⚠ No MX records found[/bold yellow]")


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain to query NS records")
def dns_ns(domain: str) -> None:
    """Get NS records for a domain."""
    console.print(f"[bold cyan]🔗 NS Records for {domain}[/bold cyan]")
    
    result = get_ns_records(domain)
    if result["ns_records"]:
        console.print(f"[bold green]✓ Nameservers:[/bold green]")
        for ns in result["ns_records"]:
            console.print(f"  • {ns}")
    else:
        if result["errors"]:
            print_errors(result["errors"])
        else:
            console.print("[bold yellow]⚠ No NS records found[/bold yellow]")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()


@cli.command()
@click.option("-d", "--domain", required=True, help="Domain/host to scan SSL/TLS certificate")
@click.option("-p", "--port", default=443, help="Port number (default 443)")
def ssl_scan(domain: str, port: int) -> None:
    """Scan SSL/TLS certificate for a host."""
    from .ssl_tls import get_certificate_info
    
    console.print(f"[bold cyan]🔐 SSL/TLS Certificate Scan for {domain}:{port}[/bold cyan]")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Scanning SSL/TLS certificate...", total=None)
        result = get_certificate_info(domain, port)
    
    if result["certificate"]:
        cert = result["certificate"]
        ssl_info = result["ssl_tls"]
        
        console.print("\n[bold green]✓ Certificate Information:[/bold green]")
        table = Table()
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        if cert["subject"]:
            subject = cert["subject"]
            table.add_row("Subject", subject.get("commonName", "N/A"))
        if cert["issuer"]:
            issuer = cert["issuer"]
            table.add_row("Issuer", issuer.get("commonName", "N/A"))
        if cert["not_before"]:
            table.add_row("Valid From", cert["not_before"])
        if cert["not_after"]:
            table.add_row("Valid Until", cert["not_after"])
        
        console.print(table)
        
        if ssl_info:
            console.print("\n[bold green]✓ SSL/TLS Information:[/bold green]")
            ssl_table = Table()
            ssl_table.add_column("Property", style="cyan")
            ssl_table.add_column("Value", style="green")
            ssl_table.add_row("Protocol", ssl_info.get("protocol_version", "N/A"))
            ssl_table.add_row("Cipher Suite", ssl_info.get("cipher_suite", "N/A"))
            ssl_table.add_row("Cipher Bits", str(ssl_info.get("cipher_bits", "N/A")))
            console.print(ssl_table)
        
        if result["issues"]:
            console.print("\n[bold yellow]⚠ Issues Found:[/bold yellow]")
            for issue in result["issues"]:
                console.print(f"  {issue}")
    else:
        if result["errors"]:
            print_errors(result["errors"])
        else:
            console.print("[bold red]✗ Failed to retrieve certificate[/bold red]")


@cli.command()
@click.option("-t", "--targets", required=True, help="File with hosts to scan (one per line)")
@click.option("-p", "--port", default=443, help="Port number (default 443)")
@click.option("--threads", default=10, help="Number of concurrent threads")
def ssl_batch(targets: str, port: int, threads: int) -> None:
    """Batch scan SSL/TLS certificates for multiple hosts."""
    from .ssl_tls import scan_ssl_tls_hosts
    
    try:
        with open(targets, "r") as f:
            hosts = [line.strip() for line in f if line.strip()]
        console.print(f"[bold cyan]🔐 SSL/TLS Batch Scan for {len(hosts)} hosts[/bold cyan]")
    except FileNotFoundError:
        console.print(f"[bold red]✗ File not found: {targets}[/bold red]")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task(f"Scanning {len(hosts)} hosts...", total=None)
        results = scan_ssl_tls_hosts(hosts, port, threads)
    
    console.print(f"\n[bold green]✓ Scanned {results['summary']['hosts_scanned']} hosts[/bold green]")
    
    for host_result in results["hosts"]:
        if host_result["issues"]:
            console.print(f"\n[bold yellow]{host_result['host']}:{host_result['port']}[/bold yellow]")
            for issue in host_result["issues"]:
                console.print(f"  {issue}")
