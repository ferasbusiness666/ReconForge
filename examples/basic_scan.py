"""Basic ReconForge example - Simple domain scan."""

from reconforge.api import ReconForgeAPI

# Initialize API
api = ReconForgeAPI()

# Scan a domain
domain = "example.com"
print(f"Scanning {domain}...")

# 1. Discover subdomains
print("\n1. Discovering subdomains...")
result = api.discover_subdomains(domain)
print(f"Found {result['count']} subdomains:")
for subdomain in result["subdomains"][:5]:
    print(f"  - {subdomain}")
if result["count"] > 5:
    print(f"  ... and {result['count'] - 5} more")

# 2. Scan ports on first subdomain
if result["subdomains"]:
    first_subdomain = result["subdomains"][0]
    print(f"\n2. Scanning ports on {first_subdomain}...")
    ports = api.scan_ports(first_subdomain)
    open_ports = [r for r in ports["results"] if r["status"] == "open"]
    print(f"Found {len(open_ports)} open ports:")
    for port_info in open_ports:
        print(f"  - Port {port_info['port']}: {port_info.get('banner', 'No banner')}")

    # 3. Detect technologies
    print(f"\n3. Detecting technologies on {first_subdomain}...")
    tech = api.detect_technologies(f"https://{first_subdomain}")
    print(f"Status: {tech['status_code']}")
    print(f"Technologies: {', '.join(tech['technologies']) or 'None detected'}")

print("\nDone!")
