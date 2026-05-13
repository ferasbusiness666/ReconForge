"""Lightweight HTTP/HTTPS reachability probing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import requests

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def extract_title(body: str) -> str:
    """Extract a compact HTML title from a response body."""
    match = TITLE_RE.search(body or "")
    if not match:
        return ""
    return " ".join(match.group(1).split())


def probe_url(url: str, timeout: float = 5.0) -> Dict[str, object]:
    """Probe one URL and return status, final URL, title, and errors."""
    row: Dict[str, object] = {"url": url, "final_url": "", "status_code": None, "title": "", "ok": False, "error": ""}
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
    except requests.exceptions.Timeout:
        row["error"] = f"Request timed out after {timeout:g} seconds."
        return row
    except requests.exceptions.SSLError as exc:
        row["error"] = f"TLS error: {exc}"
        return row
    except requests.exceptions.RequestException as exc:
        row["error"] = f"Connection error: {exc}"
        return row

    row["final_url"] = response.url
    row["status_code"] = response.status_code
    row["title"] = extract_title(response.text[:5000])
    row["ok"] = True
    return row


def probe_host(host: str, timeout: float = 5.0) -> List[Dict[str, object]]:
    """Probe HTTPS and HTTP for a host without crawling."""
    cleaned = host.strip().rstrip("/")
    if cleaned.startswith(("http://", "https://")):
        return [probe_url(cleaned, timeout=timeout)]
    return [probe_url(f"https://{cleaned}", timeout=timeout), probe_url(f"http://{cleaned}", timeout=timeout)]


def probe_hosts_file(path: str, timeout: float = 5.0) -> Dict[str, object]:
    """Probe all non-empty hosts in a file."""
    try:
        hosts = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
    except OSError as exc:
        return {"input": path, "results": [], "errors": [f"Could not read {path}: {exc}"]}

    results = []
    for host in hosts:
        results.append({"host": host, "probes": probe_host(host, timeout=timeout)})
    return {"input": path, "results": results, "errors": []}
