"""Shodan integration module for ReconForge."""

from __future__ import annotations

import requests
from typing import Dict, List, Optional


class ShodanClient:
    """Shodan API client for ReconForge."""
    
    BASE_URL = "https://api.shodan.io"
    
    def __init__(self, api_key: str):
        """Initialize Shodan client with API key."""
        self.api_key = api_key
        self.session = requests.Session()
    
    def search_host(self, query: str, page: int = 1) -> Dict:
        """Search Shodan for hosts matching query."""
        try:
            url = f"{self.BASE_URL}/shodan/host/search"
            params = {
                "query": query,
                "key": self.api_key,
                "page": page
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "matches": []}
    
    def get_host_info(self, ip: str) -> Dict:
        """Get detailed information about a host from Shodan."""
        try:
            url = f"{self.BASE_URL}/shodan/host/{ip}"
            params = {"key": self.api_key}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def search_domain(self, domain: str) -> Dict:
        """Search Shodan for a specific domain."""
        query = f"hostname:{domain}"
        return self.search_host(query)
    
    def get_account_info(self) -> Dict:
        """Get account information and plan details."""
        try:
            url = f"{self.BASE_URL}/account/profile"
            params = {"key": self.api_key}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def analyze_shodan_results(results: Dict) -> Dict:
    """Analyze Shodan search results and extract key information."""
    analysis = {
        "total_results": results.get("total", 0),
        "hosts": [],
        "services": {},
        "vulnerabilities": [],
        "high_risk": []
    }
    
    for match in results.get("matches", []):
        host_info = {
            "ip": match.get("ip_str"),
            "port": match.get("port"),
            "service": match.get("_shodan", {}).get("module", "unknown"),
            "organization": match.get("org", "Unknown"),
            "country": match.get("country_code", "Unknown"),
            "data": match.get("data", ""),
            "timestamp": match.get("timestamp"),
            "hostnames": match.get("hostnames", [])
        }
        
        # Track services
        service = host_info["service"]
        if service not in analysis["services"]:
            analysis["services"][service] = 0
        analysis["services"][service] += 1
        
        # Check for vulnerabilities
        vulns = match.get("vulns", [])
        if vulns:
            host_info["vulnerabilities"] = vulns
            analysis["vulnerabilities"].extend(vulns)
            analysis["high_risk"].append(host_info)
        
        analysis["hosts"].append(host_info)
    
    return analysis


def search_domain_on_shodan(domain: str, api_key: str) -> Dict:
    """Search for a domain on Shodan and return analyzed results."""
    client = ShodanClient(api_key)
    
    try:
        # Verify API key first
        account = client.get_account_info()
        if "error" in account:
            return {"error": f"Invalid API key: {account['error']}", "results": []}
        
        # Search for domain
        results = client.search_domain(domain)
        
        if "error" in results:
            return {"error": results["error"], "results": []}
        
        # Analyze results
        analysis = analyze_shodan_results(results)
        
        return {
            "domain": domain,
            "success": True,
            "total_results": analysis["total_results"],
            "hosts": analysis["hosts"],
            "services": analysis["services"],
            "vulnerabilities": list(set(analysis["vulnerabilities"])),
            "high_risk_hosts": analysis["high_risk"],
            "account_info": account
        }
    
    except Exception as e:
        return {"error": str(e), "results": []}


def search_ip_on_shodan(ip: str, api_key: str) -> Dict:
    """Get detailed Shodan information for an IP address."""
    client = ShodanClient(api_key)
    
    try:
        host_info = client.get_host_info(ip)
        
        if "error" in host_info:
            return {"error": host_info["error"]}
        
        # Extract key information
        result = {
            "ip": ip,
            "organization": host_info.get("org", "Unknown"),
            "country": host_info.get("country_name", "Unknown"),
            "country_code": host_info.get("country_code", "Unknown"),
            "latitude": host_info.get("latitude"),
            "longitude": host_info.get("longitude"),
            "ports": host_info.get("ports", []),
            "services": [],
            "vulnerabilities": host_info.get("vulns", []),
            "last_update": host_info.get("last_update"),
            "hostnames": host_info.get("hostnames", []),
            "domains": host_info.get("domains", [])
        }
        
        # Extract services from banners
        for banner in host_info.get("data", []):
            service = {
                "port": banner.get("port"),
                "protocol": banner.get("_shodan", {}).get("module", "unknown"),
                "data": banner.get("data", "")[:100]  # First 100 chars
            }
            result["services"].append(service)
        
        return result
    
    except Exception as e:
        return {"error": str(e)}


def generate_shodan_report(domain: str, api_key: str) -> Dict:
    """Generate a comprehensive Shodan report for a domain."""
    results = search_domain_on_shodan(domain, api_key)
    
    if "error" in results:
        return {"error": results["error"]}
    
    report = {
        "domain": domain,
        "summary": {
            "total_hosts": results["total_results"],
            "unique_services": len(results["services"]),
            "high_risk_hosts": len(results["high_risk_hosts"]),
            "total_vulnerabilities": len(results["vulnerabilities"])
        },
        "services_breakdown": results["services"],
        "high_risk_hosts": results["high_risk_hosts"],
        "vulnerabilities": results["vulnerabilities"],
        "hosts": results["hosts"]
    }
    
    return report
