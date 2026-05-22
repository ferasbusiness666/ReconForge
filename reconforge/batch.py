"""Batch processing utilities for scanning multiple targets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .portscan import scan_ports
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies


class BatchProcessor:
    """Process multiple targets in batch."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize batch processor."""
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.cwd() / "batch_results"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_domains(
        self,
        domains: List[str],
        output_file: Optional[str] = None,
        concurrent: bool = True,
    ) -> Dict[str, Any]:
        """Scan multiple domains."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domains": [],
            "summary": {
                "total_domains": len(domains),
                "successful": 0,
                "failed": 0,
            },
        }

        for domain in domains:
            print(f"Scanning {domain}...")
            domain_result = self._scan_domain(domain, concurrent=concurrent)
            results["domains"].append(domain_result)

            if domain_result.get("success"):
                results["summary"]["successful"] += 1
            else:
                results["summary"]["failed"] += 1

        # Save results
        if output_file:
            output_path = self.output_dir / output_file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {output_path}")

        return results

    def _scan_domain(self, domain: str, concurrent: bool = True) -> Dict[str, Any]:
        """Scan a single domain."""
        try:
            # Discover subdomains
            subdomains, sub_errors = fetch_subdomains(domain)

            # Scan ports
            port_results = {}
            for subdomain in subdomains[:5]:  # Limit to first 5
                scan = scan_ports(subdomain, concurrent=concurrent)
                port_results[subdomain] = scan.get("results", [])

            # Detect technologies
            tech_results = {}
            for subdomain in subdomains[:5]:
                for protocol in ["https", "http"]:
                    url = f"{protocol}://{subdomain}"
                    tech = detect_technologies(url, timeout=10.0)
                    if tech.get("status_code") or not tech.get("errors"):
                        tech_results[url] = tech
                        break

            return {
                "domain": domain,
                "success": True,
                "subdomains": subdomains,
                "ports": port_results,
                "technologies": tech_results,
                "errors": sub_errors,
            }
        except Exception as e:
            return {
                "domain": domain,
                "success": False,
                "error": str(e),
            }

    def scan_from_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        concurrent: bool = True,
    ) -> Dict[str, Any]:
        """Scan domains from a file (one per line)."""
        with open(input_file, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]

        return self.scan_domains(domains, output_file=output_file, concurrent=concurrent)

    def compare_scans(self, scan1_file: str, scan2_file: str) -> Dict[str, Any]:
        """Compare two batch scan results."""
        with open(scan1_file, "r", encoding="utf-8") as f:
            scan1 = json.load(f)

        with open(scan2_file, "r", encoding="utf-8") as f:
            scan2 = json.load(f)

        comparison = {
            "scan1_timestamp": scan1.get("timestamp"),
            "scan2_timestamp": scan2.get("timestamp"),
            "domains_added": [],
            "domains_removed": [],
            "domain_changes": {},
        }

        domains1 = {d["domain"]: d for d in scan1.get("domains", [])}
        domains2 = {d["domain"]: d for d in scan2.get("domains", [])}

        # Find added/removed domains
        comparison["domains_added"] = list(set(domains2.keys()) - set(domains1.keys()))
        comparison["domains_removed"] = list(set(domains1.keys()) - set(domains2.keys()))

        # Compare common domains
        for domain in set(domains1.keys()) & set(domains2.keys()):
            d1 = domains1[domain]
            d2 = domains2[domain]

            if d1.get("success") and d2.get("success"):
                subs1 = set(d1.get("subdomains", []))
                subs2 = set(d2.get("subdomains", []))

                comparison["domain_changes"][domain] = {
                    "new_subdomains": list(subs2 - subs1),
                    "removed_subdomains": list(subs1 - subs2),
                    "subdomain_count_change": len(subs2) - len(subs1),
                }

        return comparison

    def generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate summary of batch results."""
        report = []
        report.append("=" * 70)
        report.append("BATCH SCAN SUMMARY")
        report.append("=" * 70)
        report.append("")

        summary = results.get("summary", {})
        report.append(f"Timestamp: {results.get('timestamp')}")
        report.append(f"Total Domains: {summary.get('total_domains')}")
        report.append(f"Successful: {summary.get('successful')}")
        report.append(f"Failed: {summary.get('failed')}")
        report.append("")

        # Per-domain summary
        report.append("PER-DOMAIN RESULTS")
        report.append("-" * 70)

        for domain_result in results.get("domains", []):
            domain = domain_result.get("domain")
            success = domain_result.get("success")

            if success:
                subdomains = len(domain_result.get("subdomains", []))
                ports = sum(
                    len(p) for p in domain_result.get("ports", {}).values()
                )
                techs = len(domain_result.get("technologies", {}))

                report.append(f"{domain}: ✓")
                report.append(f"  Subdomains: {subdomains}")
                report.append(f"  Ports scanned: {ports}")
                report.append(f"  Technologies: {techs}")
            else:
                report.append(f"{domain}: ✗ ({domain_result.get('error')})")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)
