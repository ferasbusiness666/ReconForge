"""Comparison utilities for analyzing changes between scans."""

from __future__ import annotations

from typing import Any, Dict, List


class ScanComparator:
    """Compare two recon scans to identify changes."""

    def __init__(self, scan1: Dict[str, Any], scan2: Dict[str, Any]):
        """Initialize comparator with two scans."""
        self.scan1 = scan1
        self.scan2 = scan2

    def compare_subdomains(self) -> Dict[str, Any]:
        """Compare subdomains between scans."""
        subdomains1 = set(self.scan1.get("subdomains", []))
        subdomains2 = set(self.scan2.get("subdomains", []))

        new = subdomains2 - subdomains1
        removed = subdomains1 - subdomains2
        unchanged = subdomains1 & subdomains2

        return {
            "new": sorted(list(new)),
            "removed": sorted(list(removed)),
            "unchanged": sorted(list(unchanged)),
            "new_count": len(new),
            "removed_count": len(removed),
            "unchanged_count": len(unchanged),
            "total_change": len(new) + len(removed),
        }

    def compare_ports(self) -> Dict[str, Any]:
        """Compare open ports between scans."""
        ports1 = self._extract_open_ports(self.scan1)
        ports2 = self._extract_open_ports(self.scan2)

        new = ports2 - ports1
        removed = ports1 - ports2
        unchanged = ports1 & ports2

        return {
            "new": sorted(list(new)),
            "removed": sorted(list(removed)),
            "unchanged": sorted(list(unchanged)),
            "new_count": len(new),
            "removed_count": len(removed),
            "unchanged_count": len(unchanged),
            "total_change": len(new) + len(removed),
        }

    def compare_technologies(self) -> Dict[str, Any]:
        """Compare detected technologies between scans."""
        techs1 = self._extract_technologies(self.scan1)
        techs2 = self._extract_technologies(self.scan2)

        new = techs2 - techs1
        removed = techs1 - techs2
        unchanged = techs1 & techs2

        return {
            "new": sorted(list(new)),
            "removed": sorted(list(removed)),
            "unchanged": sorted(list(unchanged)),
            "new_count": len(new),
            "removed_count": len(removed),
            "unchanged_count": len(unchanged),
            "total_change": len(new) + len(removed),
        }

    def get_changes_summary(self) -> Dict[str, Any]:
        """Get summary of all changes."""
        subdomains = self.compare_subdomains()
        ports = self.compare_ports()
        technologies = self.compare_technologies()

        total_changes = (
            subdomains["total_change"]
            + ports["total_change"]
            + technologies["total_change"]
        )

        return {
            "total_changes": total_changes,
            "subdomains": subdomains,
            "ports": ports,
            "technologies": technologies,
            "has_changes": total_changes > 0,
        }

    def generate_diff_report(self) -> str:
        """Generate a detailed diff report."""
        report = []
        report.append("=" * 70)
        report.append("RECONFORGE SCAN COMPARISON REPORT")
        report.append("=" * 70)
        report.append("")

        summary = self.get_changes_summary()

        # Overall summary
        report.append(f"Total Changes: {summary['total_changes']}")
        report.append("")

        # Subdomains
        report.append("SUBDOMAINS")
        report.append("-" * 70)
        subs = summary["subdomains"]
        report.append(f"New: {subs['new_count']}")
        if subs["new"]:
            for sub in subs["new"][:10]:
                report.append(f"  + {sub}")
            if len(subs["new"]) > 10:
                report.append(f"  ... and {len(subs['new']) - 10} more")
        report.append(f"Removed: {subs['removed_count']}")
        if subs["removed"]:
            for sub in subs["removed"][:10]:
                report.append(f"  - {sub}")
            if len(subs["removed"]) > 10:
                report.append(f"  ... and {len(subs['removed']) - 10} more")
        report.append(f"Unchanged: {subs['unchanged_count']}")
        report.append("")

        # Ports
        report.append("PORTS")
        report.append("-" * 70)
        ports = summary["ports"]
        report.append(f"New: {ports['new_count']}")
        if ports["new"]:
            for port in sorted(ports["new"])[:10]:
                report.append(f"  + {port}")
            if len(ports["new"]) > 10:
                report.append(f"  ... and {len(ports['new']) - 10} more")
        report.append(f"Removed: {ports['removed_count']}")
        if ports["removed"]:
            for port in sorted(ports["removed"])[:10]:
                report.append(f"  - {port}")
            if len(ports["removed"]) > 10:
                report.append(f"  ... and {len(ports['removed']) - 10} more")
        report.append(f"Unchanged: {ports['unchanged_count']}")
        report.append("")

        # Technologies
        report.append("TECHNOLOGIES")
        report.append("-" * 70)
        techs = summary["technologies"]
        report.append(f"New: {techs['new_count']}")
        if techs["new"]:
            for tech in techs["new"][:10]:
                report.append(f"  + {tech}")
            if len(techs["new"]) > 10:
                report.append(f"  ... and {len(techs['new']) - 10} more")
        report.append(f"Removed: {techs['removed_count']}")
        if techs["removed"]:
            for tech in techs["removed"][:10]:
                report.append(f"  - {tech}")
            if len(techs["removed"]) > 10:
                report.append(f"  ... and {len(techs['removed']) - 10} more")
        report.append(f"Unchanged: {techs['unchanged_count']}")
        report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    @staticmethod
    def _extract_open_ports(scan: Dict[str, Any]) -> set:
        """Extract open ports from scan."""
        ports = set()
        for host, results in scan.get("ports", {}).items():
            for result in results:
                if result.get("status") == "open":
                    ports.add(f"{host}:{result.get('port')}")
        return ports

    @staticmethod
    def _extract_technologies(scan: Dict[str, Any]) -> set:
        """Extract technologies from scan."""
        techs = set()
        for url, result in scan.get("technologies", {}).items():
            for tech in result.get("technologies", []):
                techs.add(tech)
        return techs
