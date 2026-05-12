"""HTTP technology fingerprinting helpers."""

from __future__ import annotations

from typing import Dict, List

import requests

INTERESTING_HEADERS = [
    "Server",
    "X-Powered-By",
    "Set-Cookie",
    "Via",
    "X-Cache",
    "CF-Ray",
    "X-AspNet-Version",
    "X-Generator",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
]


def infer_technologies(headers: requests.structures.CaseInsensitiveDict, body: str) -> List[str]:
    """Infer likely technologies from response headers and a small body sample."""
    findings = set()
    server = headers.get("Server", "")
    powered_by = headers.get("X-Powered-By", "")
    cookies = headers.get("Set-Cookie", "")
    combined = " ".join([server, powered_by, cookies, body[:1000]]).lower()

    checks = {
        "nginx": "nginx",
        "apache": "Apache",
        "cloudflare": "Cloudflare",
        "express": "Express.js",
        "php": "PHP",
        "asp.net": "ASP.NET",
        "laravel": "Laravel",
        "wordpress": "WordPress",
        "react": "React",
        "next.js": "Next.js",
        "django": "Django",
        "rails": "Ruby on Rails",
    }
    for needle, label in checks.items():
        if needle in combined:
            findings.add(label)
    if headers.get("CF-Ray"):
        findings.add("Cloudflare")
    if headers.get("Strict-Transport-Security"):
        findings.add("HSTS")
    if headers.get("Content-Security-Policy"):
        findings.add("Content Security Policy")
    return sorted(findings)


def detect_technologies(url: str, timeout: float = 10.0) -> Dict[str, object]:
    """Request *url* and return structured HTTP technology fingerprints."""
    if not url or not url.strip().lower().startswith(("http://", "https://")):
        return {"url": url, "status_code": None, "headers": {}, "technologies": [], "errors": ["URL must start with http:// or https://."]}

    try:
        response = requests.get(url.strip(), timeout=timeout, allow_redirects=True)
    except requests.exceptions.Timeout:
        return {"url": url, "status_code": None, "headers": {}, "technologies": [], "errors": [f"Request timed out after {timeout:g} seconds."]}
    except requests.exceptions.SSLError as exc:
        return {"url": url, "status_code": None, "headers": {}, "technologies": [], "errors": [f"TLS error: {exc}"]}
    except requests.exceptions.RequestException as exc:
        return {"url": url, "status_code": None, "headers": {}, "technologies": [], "errors": [f"Connection error: {exc}"]}

    selected_headers = {name: response.headers[name] for name in INTERESTING_HEADERS if name in response.headers}
    return {
        "url": response.url,
        "status_code": response.status_code,
        "headers": selected_headers,
        "technologies": infer_technologies(response.headers, response.text),
        "errors": [],
    }
