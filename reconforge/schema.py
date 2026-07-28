"""Versioned metadata for ReconForge machine-readable output."""

from __future__ import annotations

from typing import Dict, Mapping

SCHEMA_VERSION = "1.0"


def with_schema(command: str, payload: Mapping[str, object]) -> Dict[str, object]:
    """Return a payload with additive command and schema metadata."""
    result = dict(payload)
    result["schema_version"] = SCHEMA_VERSION
    result["command"] = command
    return result
