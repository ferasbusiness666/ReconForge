"""Lightweight TCP port scanning and banner grabbing utilities."""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Optional

SAFE_PORTS = [80, 443, 8080, 8443, 22, 21, 3306, 6379]
NORMAL_PORTS = sorted(set(SAFE_PORTS + [3000, 5000, 5173, 8000, 8888, 9000]))
DEEP_PORTS = sorted(set(NORMAL_PORTS + [25, 53, 110, 143, 389, 445, 465, 587, 993, 995, 1433, 1521, 2049, 27017, 5432, 5601, 5900, 9200, 9300]))
SCAN_PROFILES = {"safe": SAFE_PORTS, "normal": NORMAL_PORTS, "deep": DEEP_PORTS}
COMMON_PORTS = SAFE_PORTS
HTTP_PROBE_PORTS = {80, 8080}
TLS_PROBE_PORTS = {443, 8443}


def resolve_ports(profile: str = "safe", ports_text: Optional[str] = None) -> List[int]:
    """Resolve a scan profile or comma-separated custom port list."""
    if ports_text:
        ports = []
        for raw_port in ports_text.split(","):
            cleaned = raw_port.strip()
            if not cleaned.isdigit():
                raise ValueError(f"Invalid port: {raw_port}")
            port = int(cleaned)
            if port < 1 or port > 65535:
                raise ValueError(f"Port out of range: {port}")
            ports.append(port)
        return sorted(dict.fromkeys(ports))

    if profile not in SCAN_PROFILES:
        raise ValueError(f"Unknown scan profile: {profile}")
    return list(SCAN_PROFILES[profile])


def grab_banner(sock: socket.socket, host: str, port: int, timeout: float) -> str:
    """Attempt a lightweight banner grab from an already connected socket."""
    sock.settimeout(timeout)
    try:
        if port in HTTP_PROBE_PORTS:
            sock.sendall(f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
        elif port not in TLS_PROBE_PORTS:
            try:
                sock.sendall(b"\r\n")
            except OSError:
                pass
        data = sock.recv(256)
    except socket.timeout:
        return "No banner"
    except OSError:
        return "No banner"

    decoded = data.decode("utf-8", errors="replace").strip()
    return " ".join(decoded.split()) if decoded else "No banner"


def scan_port(host: str, port: int, timeout: float = 2.0) -> Dict[str, object]:
    """Scan a single TCP *port* on *host* and return a structured result."""
    result: Dict[str, object] = {"host": host, "port": port, "status": "closed", "banner": "", "error": ""}
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            result["status"] = "open"
            result["banner"] = grab_banner(sock, host, port, timeout=min(timeout, 1.0))
    except socket.gaierror as exc:
        result["status"] = "error"
        result["error"] = f"DNS lookup failed: {exc}"
    except socket.timeout:
        result["status"] = "filtered/timeout"
        result["error"] = "Connection timed out"
    except ConnectionRefusedError:
        result["status"] = "closed"
        result["error"] = "Connection refused"
    except OSError as exc:
        result["status"] = "error"
        result["error"] = str(exc)
    return result


def _scan_port_safely(host: str, port: int, timeout: float) -> Dict[str, object]:
    """Run one port check without allowing an unexpected exception to stop a scan."""
    try:
        return scan_port(host, port, timeout=timeout)
    except Exception as exc:  # pragma: no cover - defensive boundary
        return {
            "host": host,
            "port": port,
            "status": "error",
            "banner": "",
            "error": f"Unexpected scan error: {exc}",
        }


def scan_ports(
    host: str,
    ports: Optional[List[int]] = None,
    timeout: float = 2.0,
    profile: str = "safe",
    workers: int = 8,
) -> Dict[str, object]:
    """Scan TCP ports concurrently with bounded workers and partial results."""
    try:
        targets = ports or resolve_ports(profile=profile)
    except ValueError as exc:
        return {"host": host, "results": [], "errors": [str(exc)]}
    if not host or not host.strip():
        return {"host": host, "results": [], "errors": ["Target host is required."]}

    cleaned_host = host.strip()
    normalized_targets = [int(port) for port in targets]
    max_workers = max(1, min(int(workers), len(normalized_targets), 32))
    worker = partial(_scan_port_safely, cleaned_host, timeout=timeout)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="reconforge-port") as executor:
        results = list(executor.map(worker, normalized_targets))

    errors = [
        f"{row['port']}: {row.get('error') or 'unknown socket error'}"
        for row in results
        if row.get("status") == "error"
    ]
    return {
        "host": cleaned_host,
        "results": results,
        "errors": errors,
        "workers": max_workers,
    }
