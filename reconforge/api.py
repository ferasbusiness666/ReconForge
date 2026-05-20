"""Programmatic API for ReconForge - use ReconForge in your Python code."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cache import get_cache
from .config import get_config
from .logger import get_logger
from .portscan import scan_ports
from .report import generate_report as _generate_report
from .scopecheck import check_targets
from .subdomains import fetch_subdomains
from .techdetect import detect_technologies


class ReconForgeAPI:
    """Main API class for ReconForge."""

    def __init__(self, use_cache: bool = True, log_file: Optional[str] = None):
        """Initialize ReconForge API.
        
        Args:
            use_cache: Enable result caching
            log_file: Optional log file path
        """
        self.cache = get_cache() if use_cache else None
        self.config = get_config()
        self.logger = get_logger(log_file=log_file)

    def discover_subdomains(self, domain: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Discover subdomains for a domain.
        
        Args:
            domain: Target domain
            timeout: Request timeout (uses config default if None)
        
        Returns:
            Dictionary with subdomains and errors
        """
        timeout = timeout or self.config.get("timeout", 10.0)
        
        # Check cache
        if self.cache:
            cache_key = f"subdomains:{domain}"
            cached = self.cache.get(cache_key)
            if cached:
                self.logger.info(f"Returning cached subdomains for {domain}")
                return cached
        
        self.logger.info(f"Discovering subdomains for {domain}")
        subdomains, errors = fetch_subdomains(domain, timeout=timeout)
        
        result = {
            "domain": domain,
            "subdomains": subdomains,
            "errors": errors,
            "count": len(subdomains),
        }
        
        # Cache result
        if self.cache:
            self.cache.set(cache_key, result)
        
        return result

    def scan_ports(
        self,
        host: str,
        ports: Optional[List[int]] = None,
        timeout: Optional[float] = None,
        concurrent: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Scan ports on a host.
        
        Args:
            host: Target host
            ports: List of ports to scan (uses defaults if None)
            timeout: Socket timeout (uses config default if None)
            concurrent: Use concurrent scanning (uses config default if None)
        
        Returns:
            Dictionary with scan results
        """
        timeout = timeout or self.config.get("port_scan_timeout", 2.0)
        concurrent = concurrent if concurrent is not None else self.config.get("concurrent_scanning", True)
        
        self.logger.info(f"Scanning ports on {host}")
        result = scan_ports(host, ports=ports, timeout=timeout, concurrent=concurrent)
        
        return result

    def detect_technologies(self, url: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Detect technologies on a URL.
        
        Args:
            url: Target URL
            timeout: Request timeout (uses config default if None)
        
        Returns:
            Dictionary with detected technologies
        """
        timeout = timeout or self.config.get("timeout", 10.0)
        
        self.logger.info(f"Detecting technologies on {url}")
        result = detect_technologies(url, timeout=timeout)
        
        return result

    def check_scope(self, targets_file: str, scope_file: str) -> Dict[str, Any]:
        """Check if targets are in scope.
        
        Args:
            targets_file: Path to targets file
            scope_file: Path to scope file
        
        Returns:
            Dictionary with in-scope and out-of-scope targets
        """
        self.logger.info(f"Checking scope for targets in {targets_file}")
        result = check_targets(targets_file, scope_file)
        
        return result

    def generate_report(
        self,
        domain: str,
        output: str,
        timeout: Optional[float] = None,
        max_hosts: Optional[int] = None,
        concurrent: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Generate a comprehensive recon report.
        
        Args:
            domain: Target domain
            output: Output file path
            timeout: Request timeout (uses config default if None)
            max_hosts: Maximum hosts to scan
            concurrent: Use concurrent scanning (uses config default if None)
        
        Returns:
            Dictionary with report generation results
        """
        timeout = timeout or self.config.get("timeout", 10.0)
        concurrent = concurrent if concurrent is not None else self.config.get("concurrent_scanning", True)
        
        self.logger.info(f"Generating report for {domain}")
        result = _generate_report(domain, output, timeout=timeout, max_hosts=max_hosts, concurrent=concurrent)
        
        return result

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache:
            return {"cache_enabled": False}
        
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear all cached results."""
        if self.cache:
            self.cache.clear()
            self.logger.info("Cache cleared")

    def cleanup_expired_cache(self) -> int:
        """Remove expired cache entries.
        
        Returns:
            Number of deleted entries
        """
        if not self.cache:
            return 0
        
        count = self.cache.cleanup_expired()
        self.logger.info(f"Cleaned up {count} expired cache entries")
        return count


# Convenience functions for quick access
def discover_subdomains(domain: str) -> Dict[str, Any]:
    """Quick function to discover subdomains."""
    api = ReconForgeAPI()
    return api.discover_subdomains(domain)


def scan_ports_quick(host: str) -> Dict[str, Any]:
    """Quick function to scan ports."""
    api = ReconForgeAPI()
    return api.scan_ports(host)


def detect_technologies_quick(url: str) -> Dict[str, Any]:
    """Quick function to detect technologies."""
    api = ReconForgeAPI()
    return api.detect_technologies(url)
