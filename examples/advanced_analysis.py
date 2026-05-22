"""Advanced ReconForge example - Analysis and risk assessment."""

import json
from reconforge.api import ReconForgeAPI
from reconforge.analyzer import FindingsAnalyzer
from reconforge.report import generate_report

# Initialize API
api = ReconForgeAPI()

domain = "example.com"
print(f"Advanced analysis for {domain}")
print("=" * 60)

# Generate full report
print("\nGenerating comprehensive report...")
result = api.generate_report(domain, f"{domain}_report.md")

# Read the report data
print("\nAnalyzing findings...")

# Create sample findings for analysis
findings = {
    "subdomains": api.discover_subdomains(domain)["subdomains"][:10],
    "ports": {},
    "technologies": {},
}

# Scan some subdomains
for subdomain in findings["subdomains"][:3]:
    ports = api.scan_ports(subdomain)
    findings["ports"][subdomain] = ports["results"]
    
    tech = api.detect_technologies(f"https://{subdomain}")
    findings["technologies"][f"https://{subdomain}"] = tech

# Analyze findings
analyzer = FindingsAnalyzer(findings)

# Get various analyses
print("\n1. SUBDOMAIN STATISTICS")
print("-" * 60)
stats = analyzer.get_subdomain_statistics()
print(f"Total subdomains: {stats['total_subdomains']}")
print(f"Unique prefixes: {stats['unique_prefixes']}")
print("Common prefixes:")
for prefix, count in stats["common_prefixes"][:5]:
    print(f"  - {prefix}: {count}")

print("\n2. OPEN PORTS SUMMARY")
print("-" * 60)
port_summary = analyzer.get_open_ports_summary()
print(f"Total open ports: {port_summary['total_open']}")
print(f"Unique ports: {port_summary['unique_ports']}")
print("Open ports:")
for port, hosts in port_summary["open_ports"].items():
    print(f"  - Port {port}: {len(hosts)} host(s)")

print("\n3. TECHNOLOGY SUMMARY")
print("-" * 60)
tech_summary = analyzer.get_technology_summary()
print(f"Unique technologies: {tech_summary['unique_technologies']}")
print("Most common technologies:")
for tech, count in list(tech_summary["technology_count"].items())[:5]:
    print(f"  - {tech}: {count}")

print("\n4. INTERESTING PORTS")
print("-" * 60)
interesting = analyzer.find_interesting_ports()
if interesting:
    for port_info in interesting[:10]:
        print(f"  - {port_info['host']}:{port_info['port']} ({port_info['service']})")
else:
    print("  No interesting ports found")

print("\n5. SECURITY HEADERS")
print("-" * 60)
security = analyzer.find_security_headers()
print(f"Security headers found: {len(security['found'])}")
print(f"Missing headers: {len(security['missing'])}")
print(f"Coverage: {security['coverage']:.1%}")

print("\n6. RISK ASSESSMENT")
print("-" * 60)
risk = analyzer.get_risk_assessment()
print(f"Risk Score: {risk['risk_score']}/100")
print(f"Risk Level: {risk['risk_level']}")
print("Key Findings:")
for finding in risk["findings"]:
    print(f"  - {finding}")
print("Recommendations:")
for rec in risk["recommendations"]:
    print(f"  - {rec}")

print("\n7. SUMMARY REPORT")
print("-" * 60)
summary = analyzer.generate_summary_report()
print(summary)

print("\nAnalysis complete!")
