"""AI-ready report summarization without using an AI API."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


def summarize_report(path: str, max_chars: int = 6000) -> Dict[str, object]:
    """Create a compact prompt-ready summary from a markdown report."""
    try:
        markdown = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return {"report": path, "summary": "", "errors": [f"Could not read {path}: {exc}"]}

    lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("- ") or stripped.startswith("|"):
            lines.append(stripped)

    body = "\n".join(lines)
    if len(body) > max_chars:
        body = body[:max_chars].rstrip() + "\n[truncated]"

    summary = (
        "AI-ready ReconForge summary\n\n"
        "Use this as recon context for authorized manual security testing only. "
        "Do not claim vulnerabilities without validating evidence.\n\n"
        f"{body}"
    )
    return {"report": path, "summary": summary, "errors": []}
