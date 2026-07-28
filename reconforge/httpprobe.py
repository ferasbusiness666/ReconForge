"""Lightweight HTTP/HTTPS reachability probing."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Dict, List

import requests

from .techdetect import INTERESTING_HEADERS, infer_technologies

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def extract_title(body: str) -> str:
    """Extract a compact HTML title from a response body."""
    match = TITLE_RE.search(body or "")
    if not match:
        return ""
    return " ".join(match.group(1).split())


def probe_url(url: str, timeout: float = 5.0) -> Dict[str, object]:
    """Probe one URL and return lightweight response metadata and errors."""
    row: Dict[str, object] = {
        "url": url,
        "final_url": "",
        "status_code": None,
        "title": "",
        "content_length": None,
        "content_type": "",
        "server": "",
        "technologies": [],
        "ok": False,
        "error": "",
    }
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

    body = response.text
    raw_headers = getattr(response, "headers", {})
    headers = {}
    for name in [*INTERESTING_HEADERS, "Content-Length", "Content-Type"]:
        try:
            value = raw_headers.get(name, "")
        except AttributeError:
            value = ""
        if isinstance(value, str) and value:
            headers[name] = value

    content_length = headers.get("Content-Length")
    try:
        parsed_length = int(content_length) if content_length is not None else None
    except (TypeError, ValueError):
        parsed_length = None
    if parsed_length is None:
        content = getattr(response, "content", None)
        parsed_length = len(content) if isinstance(content, (bytes, bytearray)) else len(body.encode("utf-8"))

    row["final_url"] = response.url
    row["status_code"] = response.status_code
    row["title"] = extract_title(body[:5000])
    row["content_length"] = parsed_length
    row["content_type"] = headers.get("Content-Type", "")
    row["server"] = headers.get("Server", "")
    row["technologies"] = infer_technologies(headers, body[:5000])
    row["ok"] = True
    return row


def probe_host(host: str, timeout: float = 5.0) -> List[Dict[str, object]]:
    """Probe HTTPS and HTTP for a host without crawling."""
    cleaned = host.strip().rstrip("/")
    if cleaned.startswith(("http://", "https://")):
        return [probe_url(cleaned, timeout=timeout)]
    return [probe_url(f"https://{cleaned}", timeout=timeout), probe_url(f"http://{cleaned}", timeout=timeout)]


def _probe_host_safely(host: str, timeout: float) -> Dict[str, object]:
    """Probe one host without allowing an unexpected exception to stop the batch."""
    try:
        return {"host": host, "probes": probe_host(host, timeout=timeout), "error": ""}
    except Exception as exc:  # pragma: no cover - defensive boundary
        return {"host": host, "probes": [], "error": str(exc)}


def probe_hosts_file(path: str, timeout: float = 5.0, workers: int = 8) -> Dict[str, object]:
    """Probe all non-empty hosts concurrently with bounded workers."""
    try:
        hosts = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
    except OSError as exc:
        return {"input": path, "results": [], "errors": [f"Could not read {path}: {exc}"]}

    if not hosts:
        return {"input": path, "results": [], "errors": [], "workers": 0}

    max_workers = max(1, min(int(workers), len(hosts), 32))
    worker = partial(_probe_host_safely, timeout=timeout)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="reconforge-http") as executor:
        results = list(executor.map(worker, hosts))

    errors = [
        f"{row['host']}: {row['error']}"
        for row in results
        if row.get("error")
    ]
    return {
        "input": path,
        "results": results,
        "errors": errors,
        "workers": max_workers,
    }
