"""Output helpers for CLI and report file writing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def ensure_parent(path: str) -> Path:
    """Create the parent directory for *path* and return a Path object."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def write_json(path: str, data: object) -> str:
    """Write *data* as stable JSON and return the output path."""
    output_path = ensure_parent(path)
    output_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return str(output_path)


def write_lines(path: str, lines: Iterable[object]) -> str:
    """Write one item per line and return the output path."""
    output_path = ensure_parent(path)
    output_path.write_text("\n".join(str(line) for line in lines) + "\n", encoding="utf-8")
    return str(output_path)


def write_text(path: str, text: str) -> str:
    """Write text and return the output path."""
    output_path = ensure_parent(path)
    output_path.write_text(text, encoding="utf-8")
    return str(output_path)
