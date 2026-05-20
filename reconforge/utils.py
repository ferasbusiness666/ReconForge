"""Utility functions for ReconForge."""

from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import urlparse


def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IPv4 address."""
    pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip.strip()))


def is_valid_cidr(cidr: str) -> bool:
    """Check if string is a valid CIDR notation."""
    try:
        import ipaddress
        ipaddress.ip_network(cidr, strict=False)
        return True
    except (ValueError, ipaddress.AddressValueError):
        return False


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or None
    except Exception:
        return None


def extract_port_from_url(url: str) -> Optional[int]:
    """Extract port from URL."""
    try:
        parsed = urlparse(url)
        return parsed.port
    except Exception:
        return None


def normalize_url(url: str) -> str:
    """Normalize URL for consistent comparison."""
    url = url.strip().lower()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def parse_port_list(port_string: str) -> List[int]:
    """Parse comma-separated port list into list of integers."""
    ports = []
    try:
        for part in port_string.split(","):
            part = part.strip()
            if "-" in part:
                # Handle port ranges like 8000-8100
                start, end = part.split("-")
                ports.extend(range(int(start), int(end) + 1))
            else:
                ports.append(int(part))
    except (ValueError, AttributeError):
        return []
    return sorted(list(set(ports)))


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_duration(seconds: float) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    return sanitized or "output"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def deduplicate_list(items: List[str]) -> List[str]:
    """Deduplicate list while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
