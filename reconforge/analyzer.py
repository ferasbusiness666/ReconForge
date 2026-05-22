"""Advanced analysis and filtering utilities for ReconForge findings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class FindingsAnalyzer:
    """Analyze and filter recon findings for insights."""

    def __init__(self, findings: Dict[str, Any]):
        """Initialize analyzer with findings."""
        self.findings = findings
        self.subdomains = findings.get("subdomains", [])
        self.ports = findings.get("ports", {})
        self.technologies = findings.get("technologies", {})

    def get_open_ports_summary(self) -> Dict[str, Any]:
        """Get summary of open ports across all hosts."""
        open_ports = {}
        port_count = {}

        for host, results in self.ports.items():
            for result in results:
                if result.get("status") == "open":
                    port = result.get("port")
                    if port not in open_ports:
                        open_ports[port] = []
                        port_count[port] = 0
                    open_ports[port].append(host)
                    port_count[port] += 1

        return {
            "open_ports": open_ports,
            "port_count": port_count,
            "total_open": sum(port_count.values()),
            "unique_ports": len(open_ports),
        }

    def get_technology_summary(self) -> Dict[str, Any]:
        """Get summary of detected technologies."""
        tech_count = {}
        tech_hosts = {}

        for url, result in self.technologies.items():
            for tech in result.get("technologies", []):
                if tech not in tech_count:
                    tech_count[tech] = 0
                    tech_hosts[tech] = []
                tech_count[tech] += 1
                tech_hosts[tech].append(url)

        # Sort by frequency
        sorted_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)

        return {
            "technology_count": dict(sorted_techs),
            "technology_hosts": tech_hosts,
            "unique_technologies": len(tech_count),
            "most_common": sorted_techs[0][0] if sorted_techs else None,
        }

    def find_interesting_ports(self) -> List[Dict[str, Any]]:
        """Find potentially interesting open ports."""
        interesting = {
            80: "HTTP",
            443: "HTTPS",
            8080: "HTTP Alt",
            8443: "HTTPS Alt",
            3000: "Node.js",
            5000: "Flask/Dev",
            8000: "Django/Dev",
            9000: "SonarQube",
            27017: "MongoDB",
            6379: "Redis",
            5432: "PostgreSQL",
            3306: "MySQL",
            1433: "MSSQL",
            22: "SSH",
            21: "FTP",
            25: "SMTP",
            110: "POP3",
            143: "IMAP",
        }

        found = []
        for host, results in self.ports.items():
            for result in results:
                if result.get("status") == "open":
                    port = result.get("port")
                    if port in interesting:
                        found.append({
                            "host": host,
                            "port": port,
                            "service": interesting[port],
                            "banner": result.get("banner", ""),
                        })

        return sorted(found, key=lambda x: x["port"])

    def find_security_headers(self) -> Dict[str, Any]:
        """Analyze security headers across all URLs."""
        security_headers = {
            "Strict-Transport-Security": "HSTS",
            "Content-Security-Policy": "CSP",
            "X-Content-Type-Options": "X-Content-Type-Options",
            "X-Frame-Options": "Clickjacking Protection",
            "X-XSS-Protection": "XSS Protection",
            "Referrer-Policy": "Referrer Policy",
            "Permissions-Policy": "Permissions Policy",
        }

        found = {}
        missing = {}

        for url, result in self.technologies.items():
            headers = result.get("headers", {})
            for header, name in security_headers.items():
                if header in headers:
                    if name not in found:
                        found[name] = []
                    found[name].append(url)
                else:
                    if name not in missing:
                        missing[name] = []
                    missing[name].append(url)

        return {
            "found": found,
            "missing": missing,
            "coverage": len(found) / len(security_headers) if security_headers else 0,
        }

    def find_potential_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Find potential vulnerability indicators."""
        vulnerabilities = []

        # Check for outdated technologies
        outdated_patterns = {
            "Apache/2.2": "Outdated Apache",
            "nginx/1.0": "Outdated nginx",
            "PHP/5": "Outdated PHP",
            "jQuery/1": "Outdated jQuery",
        }

        for url, result in self.technologies.items():
            headers = result.get("headers", {})
            server = headers.get("Server", "")

            for pattern, vuln in outdated_patterns.items():
                if pattern.lower() in server.lower():
                    vulnerabilities.append({
                        "url": url,
                        "type": "Outdated Software",
                        "finding": vuln,
                        "severity": "Medium",
                    })

        # Check for missing security headers
        security_check = self.find_security_headers()
        for header, urls in security_check["missing"].items():
            if urls:
                vulnerabilities.append({
                    "url": urls[0] if urls else "Unknown",
                    "type": "Missing Security Header",
                    "finding": f"Missing {header}",
                    "severity": "Low",
                    "affected_urls": len(urls),
                })

        return vulnerabilities

    def get_subdomain_statistics(self) -> Dict[str, Any]:
        """Get statistics about discovered subdomains."""
        subdomain_patterns = {}
        for subdomain in self.subdomains:
            parts = subdomain.split(".")
            if len(parts) > 2:
                prefix = parts[0]
                if prefix not in subdomain_patterns:
                    subdomain_patterns[prefix] = 0
                subdomain_patterns[prefix] += 1

        return {
            "total_subdomains": len(self.subdomains),
            "unique_prefixes": len(subdomain_patterns),
            "common_prefixes": sorted(
                subdomain_patterns.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get overall risk assessment."""
        score = 0
        findings = []

        # Check for open ports
        open_summary = self.get_open_ports_summary()
        if open_summary["total_open"] > 5:
            score += 20
            findings.append(f"Many open ports detected ({open_summary['total_open']})")

        # Check for common vulnerable ports
        vulnerable_ports = [3306, 27017, 6379, 5432, 1433]
        for port in vulnerable_ports:
            if port in open_summary["open_ports"]:
                score += 15
                findings.append(f"Potentially exposed database port: {port}")

        # Check for missing security headers
        security = self.find_security_headers()
        if security["coverage"] < 0.5:
            score += 25
            findings.append("Missing multiple security headers")

        # Check for outdated software
        vulns = self.find_potential_vulnerabilities()
        if vulns:
            score += 10 * len(vulns)
            findings.append(f"Found {len(vulns)} potential vulnerability indicators")

        # Normalize score to 0-100
        score = min(score, 100)

        risk_level = "Low" if score < 30 else "Medium" if score < 70 else "High"

        return {
            "risk_score": score,
            "risk_level": risk_level,
            "findings": findings,
            "recommendations": self._get_recommendations(risk_level),
        }

    def _get_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on risk level."""
        recommendations = []

        if risk_level == "High":
            recommendations.extend([
                "Conduct thorough security assessment",
                "Review exposed services and ports",
                "Implement security headers",
                "Update outdated software",
                "Consider WAF deployment",
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Review security configuration",
                "Add missing security headers",
                "Update software to latest versions",
                "Implement additional monitoring",
            ])
        else:
            recommendations.extend([
                "Continue security monitoring",
                "Keep software updated",
                "Maintain security headers",
            ])

        return recommendations

    def generate_summary_report(self) -> str:
        """Generate a text summary of findings."""
        report = []
        report.append("=" * 60)
        report.append("RECONFORGE ANALYSIS SUMMARY")
        report.append("=" * 60)
        report.append("")

        # Subdomain stats
        subdomain_stats = self.get_subdomain_statistics()
        report.append(f"Subdomains: {subdomain_stats['total_subdomains']}")
        report.append(f"Unique Prefixes: {subdomain_stats['unique_prefixes']}")
        report.append("")

        # Open ports
        port_summary = self.get_open_ports_summary()
        report.append(f"Open Ports: {port_summary['total_open']}")
        report.append(f"Unique Ports: {port_summary['unique_ports']}")
        report.append("")

        # Technologies
        tech_summary = self.get_technology_summary()
        report.append(f"Technologies Detected: {tech_summary['unique_technologies']}")
        if tech_summary["most_common"]:
            report.append(f"Most Common: {tech_summary['most_common']}")
        report.append("")

        # Risk assessment
        risk = self.get_risk_assessment()
        report.append(f"Risk Score: {risk['risk_score']}/100")
        report.append(f"Risk Level: {risk['risk_level']}")
        report.append("")

        if risk["findings"]:
            report.append("Key Findings:")
            for finding in risk["findings"]:
                report.append(f"  - {finding}")
            report.append("")

        if risk["recommendations"]:
            report.append("Recommendations:")
            for rec in risk["recommendations"]:
                report.append(f"  - {rec}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
