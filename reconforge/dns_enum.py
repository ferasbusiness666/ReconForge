"""DNS enumeration module for ReconForge."""

from __future__ import annotations

import socket
import dns.resolver
import dns.rdatatype
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed


def resolve_dns(domain: str, record_type: str = "A", timeout: float = 5.0) -> Dict[str, object]:
    """Resolve DNS records for a domain.
    
    Args:
        domain: Domain to resolve
        record_type: DNS record type (A, AAAA, MX, NS, TXT, CNAME, SOA)
        timeout: Query timeout in seconds
    
    Returns:
        Dictionary with resolved records and errors
    """
    results = {"records": [], "errors": []}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        answers = resolver.resolve(domain, record_type)
        for rdata in answers:
            results["records"].append(str(rdata))
    except dns.resolver.NXDOMAIN:
        results["errors"].append(f"Domain {domain} does not exist")
    except dns.resolver.NoAnswer:
        results["errors"].append(f"No {record_type} records found for {domain}")
    except dns.exception.Timeout:
        results["errors"].append(f"DNS query timeout for {domain}")
    except Exception as e:
        results["errors"].append(f"DNS resolution error: {str(e)}")
    
    return results


def enumerate_dns_records(domain: str, timeout: float = 5.0) -> Dict[str, object]:
    """Enumerate all common DNS records for a domain.
    
    Args:
        domain: Domain to enumerate
        timeout: Query timeout in seconds
    
    Returns:
        Dictionary with all DNS records
    """
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV"]
    results = {}
    errors = []
    
    for record_type in record_types:
        result = resolve_dns(domain, record_type, timeout)
        if result["records"]:
            results[record_type] = result["records"]
        errors.extend(result["errors"])
    
    return {"records": results, "errors": errors}


def brute_force_subdomains(
    domain: str,
    wordlist: Optional[List[str]] = None,
    timeout: float = 2.0,
    max_workers: int = 10
) -> Dict[str, object]:
    """Brute force DNS subdomains using a wordlist.
    
    Args:
        domain: Base domain
        wordlist: List of subdomain prefixes to try
        timeout: Query timeout in seconds
        max_workers: Number of concurrent threads
    
    Returns:
        Dictionary with found subdomains
    """
    if not wordlist:
        # Common subdomains to try
        wordlist = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop",
            "ns1", "webdisk", "ns2", "cpanel", "whm", "autodiscover",
            "autoconfig", "m", "imap", "test", "portal", "ns", "vpn",
            "admin", "api", "dev", "staging", "prod", "production",
            "backup", "cdn", "git", "jenkins", "grafana", "kibana",
            "prometheus", "elastic", "mongo", "mysql", "postgres", "redis",
            "cache", "db", "database", "sql", "ldap", "kerberos",
            "auth", "oauth", "saml", "sso", "idp", "iam", "vault",
            "secrets", "config", "consul", "etcd", "zookeeper", "kafka",
            "rabbitmq", "activemq", "nats", "mqtt", "amqp", "stomp"
        ]
    
    found_subdomains: Set[str] = set()
    errors: List[str] = []
    
    def check_subdomain(prefix: str) -> Optional[str]:
        """Check if a subdomain resolves."""
        subdomain = f"{prefix}.{domain}"
        try:
            socket.gethostbyname(subdomain)
            return subdomain
        except socket.gaierror:
            return None
        except Exception as e:
            errors.append(f"Error checking {subdomain}: {str(e)}")
            return None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_subdomain, prefix): prefix for prefix in wordlist}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found_subdomains.add(result)
    
    return {
        "subdomains": sorted(list(found_subdomains)),
        "count": len(found_subdomains),
        "errors": errors
    }


def reverse_dns_lookup(ip: str, timeout: float = 5.0) -> Dict[str, object]:
    """Perform reverse DNS lookup on an IP address.
    
    Args:
        ip: IP address to lookup
        timeout: Query timeout in seconds
    
    Returns:
        Dictionary with reverse DNS results
    """
    results = {"hostname": None, "errors": []}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        # Reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip)
        results["hostname"] = hostname
    except socket.herror:
        results["errors"].append(f"No reverse DNS record found for {ip}")
    except Exception as e:
        results["errors"].append(f"Reverse DNS lookup error: {str(e)}")
    
    return results


def get_mx_records(domain: str, timeout: float = 5.0) -> Dict[str, object]:
    """Get MX records for a domain (useful for email enumeration).
    
    Args:
        domain: Domain to query
        timeout: Query timeout in seconds
    
    Returns:
        Dictionary with MX records
    """
    results = {"mx_records": [], "errors": []}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        answers = resolver.resolve(domain, "MX")
        for rdata in answers:
            results["mx_records"].append({
                "preference": rdata.preference,
                "exchange": str(rdata.exchange)
            })
    except dns.resolver.NXDOMAIN:
        results["errors"].append(f"Domain {domain} does not exist")
    except dns.resolver.NoAnswer:
        results["errors"].append(f"No MX records found for {domain}")
    except Exception as e:
        results["errors"].append(f"MX lookup error: {str(e)}")
    
    return results


def get_ns_records(domain: str, timeout: float = 5.0) -> Dict[str, object]:
    """Get NS records for a domain.
    
    Args:
        domain: Domain to query
        timeout: Query timeout in seconds
    
    Returns:
        Dictionary with NS records
    """
    results = {"ns_records": [], "errors": []}
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        answers = resolver.resolve(domain, "NS")
        for rdata in answers:
            results["ns_records"].append(str(rdata))
    except dns.resolver.NXDOMAIN:
        results["errors"].append(f"Domain {domain} does not exist")
    except dns.resolver.NoAnswer:
        results["errors"].append(f"No NS records found for {domain}")
    except Exception as e:
        results["errors"].append(f"NS lookup error: {str(e)}")
    
    return results
