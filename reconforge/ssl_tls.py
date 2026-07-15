"""SSL/TLS certificate analysis module for ReconForge."""

from __future__ import annotations

import socket
import ssl
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_certificate_info(host: str, port: int = 443, timeout: float = 5.0) -> Dict:
    """Get SSL/TLS certificate information for a host."""
    result = {
        "host": host,
        "port": port,
        "certificate": None,
        "ssl_tls": None,
        "issues": [],
        "errors": []
    }
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                
                result["certificate"] = {
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "version": cert.get("version"),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                }
                
                result["ssl_tls"] = {
                    "protocol_version": version,
                    "cipher_suite": cipher[0],
                    "cipher_bits": cipher[2],
                }
                
                _check_certificate_issues(result, cert)
                _check_ssl_tls_issues(result, version, cipher)
                
    except ssl.SSLError as e:
        result["errors"].append(f"SSL Error: {str(e)}")
    except socket.timeout:
        result["errors"].append(f"Connection timeout")
    except socket.gaierror:
        result["errors"].append(f"Cannot resolve hostname")
    except Exception as e:
        result["errors"].append(f"Error: {str(e)}")
    
    return result


def _check_certificate_issues(result: Dict, cert: Dict) -> None:
    """Check for certificate-related issues."""
    try:
        not_after_str = cert.get("notAfter", "")
        if not_after_str:
            not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
            days_until_expiry = (not_after - datetime.now()).days
            
            if days_until_expiry < 0:
                result["issues"].append("❌ Certificate has expired")
            elif days_until_expiry < 30:
                result["issues"].append(f"⚠️  Certificate expires in {days_until_expiry} days")
            else:
                result["issues"].append(f"✅ Certificate valid for {days_until_expiry} days")
        
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        
        if subject == issuer:
            result["issues"].append("⚠️  Self-signed certificate")
            
    except Exception as e:
        result["errors"].append(f"Certificate check error: {str(e)}")


def _check_ssl_tls_issues(result: Dict, version: str, cipher: tuple) -> None:
    """Check for SSL/TLS-related issues."""
    if version in ("SSLv2", "SSLv3"):
        result["issues"].append(f"❌ Deprecated: {version}")
    elif version == "TLSv1":
        result["issues"].append(f"⚠️  Weak: {version}")
    elif version in ("TLSv1.2", "TLSv1.3"):
        result["issues"].append(f"✅ Strong: {version}")
    
    cipher_bits = cipher[2]
    if cipher_bits < 128:
        result["issues"].append(f"❌ Weak cipher ({cipher_bits} bits)")
    elif cipher_bits >= 256:
        result["issues"].append(f"✅ Strong cipher ({cipher_bits} bits)")


def scan_ssl_tls_hosts(hosts: List[str], port: int = 443, max_workers: int = 10) -> Dict:
    """Scan multiple hosts for SSL/TLS issues."""
    results = {"hosts": [], "summary": {}}
    
    def scan_host(host: str) -> Dict:
        return get_certificate_info(host, port)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_host, host): host for host in hosts}
        for future in as_completed(futures):
            try:
                result = future.result()
                results["hosts"].append(result)
            except Exception:
                pass
    
    results["summary"] = {
        "total_hosts": len(hosts),
        "hosts_scanned": len(results["hosts"]),
    }
    
    return results
