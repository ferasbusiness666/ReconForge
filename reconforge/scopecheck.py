"""Scope validation helpers for recon targets."""

from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Dict, List, Tuple


def read_entries(path: str) -> Tuple[List[str], List[str]]:
    """Read non-empty, non-comment entries from *path*."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"Could not read {path}: {exc}"]

    entries = []
    for line in lines:
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            entries.append(cleaned)
    return entries, []


def normalize_host(value: str) -> str:
    """Normalize a target or scope hostname by removing schemes and paths."""
    cleaned = value.strip().lower()
    had_scheme = False
    for prefix in ("http://", "https://"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            had_scheme = True
    if had_scheme or "/" not in cleaned:
        cleaned = cleaned.split("/", 1)[0]
    cleaned = cleaned.split(":", 1)[0].rstrip(".")
    return cleaned


def target_matches_scope(target: str, scope_entry: str) -> Tuple[bool, str]:
    """Return whether *target* matches *scope_entry* and why."""
    target_host = normalize_host(target)
    scope_host = normalize_host(scope_entry)

    try:
        target_ip = ipaddress.ip_address(target_host)
    except ValueError:
        target_ip = None

    try:
        if "/" in scope_host:
            network = ipaddress.ip_network(scope_host, strict=False)
            if target_ip and target_ip in network:
                return True, f"matched CIDR {network}"
            return False, ""
        scope_ip = ipaddress.ip_address(scope_host)
        if target_ip and target_ip == scope_ip:
            return True, f"matched IP {scope_ip}"
        return False, ""
    except ValueError:
        pass

    if scope_host.startswith("*."):
        base = scope_host[2:]
        if target_host.endswith(f".{base}") and target_host != base:
            return True, f"matched wildcard {scope_host}"
        return False, ""

    if target_host == scope_host:
        return True, f"matched exact host {scope_host}"
    return False, ""


def check_targets(targets_file: str, scope_file: str) -> Dict[str, object]:
    """Compare target entries against a scope file and separate safe results."""
    targets, target_errors = read_entries(targets_file)
    scopes, scope_errors = read_entries(scope_file)
    errors = target_errors + scope_errors
    in_scope = []
    out_of_scope = []

    if errors:
        return {"in_scope": in_scope, "out_of_scope": out_of_scope, "errors": errors}

    for target in targets:
        if not normalize_host(target):
            out_of_scope.append({"target": target, "reason": "malformed target"})
            continue
        matched = False
        malformed_scopes = []
        for scope in scopes:
            if not normalize_host(scope):
                malformed_scopes.append(scope)
                continue
            is_match, reason = target_matches_scope(target, scope)
            if is_match:
                in_scope.append({"target": target, "reason": reason})
                matched = True
                break
        if not matched:
            reason = "no scope rule matched"
            if malformed_scopes:
                reason += f"; ignored malformed scope entries: {', '.join(malformed_scopes)}"
            out_of_scope.append({"target": target, "reason": reason})

    return {"in_scope": in_scope, "out_of_scope": out_of_scope, "errors": errors}
