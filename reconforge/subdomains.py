"""Subdomain discovery helpers backed by lightweight public sources."""

from __future__ import annotations

import re
import socket
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable, Dict, Iterable, List, Tuple

import requests

CRT_SH_URL = "https://crt.sh/"
HACKERTARGET_URL = "https://api.hackertarget.com/hostsearch/"
CERTSPOTTER_URL = "https://api.certspotter.com/v1/issuances"
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


def name_candidates(raw_value: object) -> Iterable[str]:
    """Yield possible DNS names from provider-specific string or list values."""
    if isinstance(raw_value, str):
        for line in raw_value.replace(",", "\n").splitlines():
            cleaned = line.strip()
            if cleaned:
                yield cleaned
    elif isinstance(raw_value, list):
        for item in raw_value:
            yield from name_candidates(item)


def keep_subdomain(candidate: str, domain: str) -> str:
    """Return a normalized in-domain host or an empty string when invalid."""
    normalized = normalize_name(candidate)
    if not normalized:
        return ""
    if normalized == domain or normalized.endswith(f".{domain}"):
        return normalized
    return ""


def query_crtsh(domain: str, timeout: float) -> Tuple[List[str], List[str]]:
    """Query crt.sh and return raw hostnames plus provider errors."""
    response = requests.get(
        CRT_SH_URL,
        params={"q": f"%.{domain}", "output": "json"},
        timeout=timeout,
    )
    response.raise_for_status()

    try:
        rows = response.json()
    except ValueError:
        return [], ["crt.sh returned malformed JSON."]

    if not isinstance(rows, list):
        return [], ["crt.sh returned an unexpected JSON structure."]

    names = []
    for row in rows:
        if isinstance(row, dict):
            names.extend(name_candidates(row.get("name_value", "")))
    return names, []


def query_hackertarget(domain: str, timeout: float) -> Tuple[List[str], List[str]]:
    """Query HackerTarget hostsearch and return raw hostnames plus errors."""
    response = requests.get(HACKERTARGET_URL, params={"q": domain}, timeout=timeout)
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        return [], []
    if text.lower().startswith(("error", "api count exceeded")):
        return [], [f"HackerTarget hostsearch returned: {text}"]

    names = []
    for line in text.splitlines():
        host = line.split(",", 1)[0].strip()
        if host:
            names.append(host)
    return names, []


def query_certspotter(domain: str, timeout: float) -> Tuple[List[str], List[str]]:
    """Query Cert Spotter's public endpoint and return raw DNS names plus errors."""
    response = requests.get(
        CERTSPOTTER_URL,
        params={"domain": domain, "include_subdomains": "true", "expand": "dns_names"},
        timeout=timeout,
    )
    response.raise_for_status()

    try:
        rows = response.json()
    except ValueError:
        return [], ["Cert Spotter returned malformed JSON."]

    if not isinstance(rows, list):
        return [], ["Cert Spotter returned an unexpected JSON structure."]

    names = []
    for row in rows:
        if isinstance(row, dict):
            names.extend(name_candidates(row.get("dns_names", [])))
    return names, []


PROVIDERS: List[Tuple[str, Callable[[str, float], Tuple[List[str], List[str]]]]] = [
    ("crt.sh", query_crtsh),
    ("HackerTarget hostsearch", query_hackertarget),
    ("Cert Spotter", query_certspotter),
]


def fetch_subdomains(domain: str, timeout: float = 15.0) -> Tuple[List[str], List[str]]:
    """Fetch, normalize, deduplicate, and sort subdomains for *domain*.

    Returns a tuple of ``(subdomains, errors)`` so callers can surface clear
    user-facing messages without raising tracebacks for expected network or data
    problems.
    """
    cleaned_domain = domain.strip().lower().rstrip(".") if domain else ""
    if not is_valid_domain(cleaned_domain):
        return [], [f"Invalid domain: {domain!r}"]

    discovered = set()
    errors: List[str] = []
    for provider_name, provider in PROVIDERS:
        try:
            names, provider_errors = provider(cleaned_domain, timeout)
        except requests.exceptions.Timeout:
            errors.append(f"{provider_name} request timed out after {timeout:g} seconds.")
            continue
        except requests.exceptions.RequestException as exc:
            errors.append(f"{provider_name} request failed: {exc}")
            continue

        errors.extend(provider_errors)
        for raw_name in names:
            normalized = keep_subdomain(raw_name, cleaned_domain)
            if normalized:
                discovered.add(normalized)

    return sorted(discovered), errors


def _resolve_hostname(hostname: str) -> Tuple[str, List[str], str]:
    """Resolve one hostname with the operating system DNS resolver."""
    try:
        answers = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return hostname, [], ""
    except OSError as exc:
        return hostname, [], str(exc)

    addresses = sorted({str(answer[4][0]) for answer in answers if answer[4]})
    return hostname, addresses, ""


def filter_resolvable(
    hostnames: Iterable[str],
    workers: int = 8,
) -> Tuple[List[str], Dict[str, List[str]], List[str]]:
    """Keep hostnames that resolve, using bounded standard-library DNS checks."""
    candidates = sorted(set(hostnames))
    if not candidates:
        return [], {}, []

    max_workers = max(1, min(int(workers), len(candidates), 32))
    worker = partial(_resolve_hostname)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="reconforge-dns") as executor:
        rows = list(executor.map(worker, candidates))

    resolutions = {hostname: addresses for hostname, addresses, _error in rows if addresses}
    errors = [f"DNS resolution error for {hostname}: {error}" for hostname, _addresses, error in rows if error]
    return sorted(resolutions), resolutions, errors


def subdomain_rows(domain: str, timeout: float = 15.0) -> Dict[str, object]:
    """Return subdomain discovery results in a structured dictionary."""
    subdomains, errors = fetch_subdomains(domain, timeout=timeout)
    return {"domain": domain, "subdomains": subdomains, "errors": errors}
