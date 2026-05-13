"""Small JSON config loader for ReconForge defaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple


def load_config(path: str = "reconforge.json") -> Tuple[Dict[str, object], list[str]]:
    """Load an optional JSON config file, returning config and errors."""
    config_path = Path(path)
    if not config_path.exists():
        return {}, []
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, [f"Could not read config {path}: {exc}"]
    except ValueError as exc:
        return {}, [f"Invalid JSON config {path}: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"Invalid config {path}: expected a JSON object."]
    return data, []


def config_section(config: Dict[str, object], name: str) -> Dict[str, object]:
    """Return a named config section when it is an object."""
    value = config.get(name)
    return value if isinstance(value, dict) else {}
