"""Subdomain discovery helpers backed by crt.sh certificate transparency data."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

import requests

CRT_SH_URL = "https://crt.sh/"
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$")


def is_valid_domain(domain: str) -> bool:
    """Return True when *domain* looks like a valid DNS domain name."""
    return bool(domain and DOMAIN_RE.match(domain.strip().rstrip(".")))


def normalize_name(name: str) -> str:
    """Normalize a certificate DNS name to lowercase without wildcard prefixes."""
    normalized = name.strip().lower().rstrip(".")
    while normalized.startswith("*."):
        normalized = normalized[2:]
    return normalized


def fetch_subdomains(domain: str, timeout: float = 15.0) -> Tuple[List[str], List[str]]:
    """Fetch, normalize, deduplicate, and sort subdomains for *domain* from crt.sh.

    Returns a tuple of ``(subdomains, errors)`` so callers can surface clear
    user-facing messages without raising tracebacks for expected network or data
    problems.
    """
    cleaned_domain = domain.strip().lower().rstrip(".") if domain else ""
    if not is_valid_domain(cleaned_domain):
        return [], [f"Invalid domain: {domain!r}"]

    try:
        response = requests.get(
            CRT_SH_URL,
            params={"q": f"%.{cleaned_domain}", "output": "json"},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return [], [f"crt.sh request timed out after {timeout:g} seconds."]
    except requests.exceptions.RequestException as exc:
        return [], [f"crt.sh request failed: {exc}"]

    try:
        rows = response.json()
    except ValueError:
        return [], ["crt.sh returned malformed JSON."]

    if not isinstance(rows, list):
        return [], ["crt.sh returned an unexpected JSON structure."]

    discovered = set()
    errors: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name_value = row.get("name_value", "")
        if not isinstance(name_value, str):
            continue
        for raw_name in name_value.splitlines():
            normalized = normalize_name(raw_name)
            if not normalized:
                continue
            if normalized == cleaned_domain or normalized.endswith(f".{cleaned_domain}"):
                discovered.add(normalized)

    return sorted(discovered), errors


def subdomain_rows(domain: str, timeout: float = 15.0) -> Dict[str, object]:
    """Return subdomain discovery results in a structured dictionary."""
    subdomains, errors = fetch_subdomains(domain, timeout=timeout)
    return {"domain": domain, "subdomains": subdomains, "errors": errors}
