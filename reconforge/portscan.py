"""Lightweight TCP port scanning and banner grabbing utilities."""

from __future__ import annotations

import socket
from typing import Dict, List, Optional

COMMON_PORTS = [80, 443, 8080, 8443, 22, 21, 3306, 6379]
HTTP_PROBE_PORTS = {80, 8080}
TLS_PROBE_PORTS = {443, 8443}


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
        return "No banner (timeout)"
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
        result["status"] = "closed"
        result["error"] = "Connection timed out"
    except OSError as exc:
        result["status"] = "closed"
        result["error"] = str(exc)
    return result


def scan_ports(host: str, ports: Optional[List[int]] = None, timeout: float = 2.0) -> Dict[str, object]:
    """Scan common TCP ports on *host* with socket timeouts."""
    targets = ports or COMMON_PORTS
    if not host or not host.strip():
        return {"host": host, "results": [], "errors": ["Target host is required."]}

    results = []
    errors = []
    for port in targets:
        row = scan_port(host.strip(), int(port), timeout=timeout)
        if row["status"] == "error":
            errors.append(str(row["error"]))
            results.append(row)
            break
        results.append(row)
    return {"host": host.strip(), "results": results, "errors": errors}
