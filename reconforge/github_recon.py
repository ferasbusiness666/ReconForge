"""GitHub public API recon helpers."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

import requests

GITHUB_API = "https://api.github.com"
INTERESTING_FILES = [
    "README.md",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
    "SECURITY.md",
    "CODEOWNERS",
    ".github/dependabot.yml",
    ".github/dependabot.yaml",
    "go.mod",
    "Cargo.toml",
    "next.config.js",
    "next.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "vercel.json",
    "netlify.toml",
    "render.yaml",
    "Procfile",
    "serverless.yml",
    "serverless.yaml",
    "Chart.yaml",
    "kustomization.yaml",
    "terraform/main.tf",
    "main.tf",
]


def github_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Build GitHub API headers, optionally using a token without logging it."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ReconForge",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _integer_header(headers: object, name: str) -> Optional[int]:
    """Read an integer HTTP header without raising on malformed values."""
    try:
        value = headers.get(name)  # type: ignore[union-attr]
        return int(value) if value is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def _rate_limit_details(headers: object) -> Dict[str, Optional[int]]:
    """Return normalized GitHub rate-limit header values."""
    return {
        "limit": _integer_header(headers, "X-RateLimit-Limit"),
        "remaining": _integer_header(headers, "X-RateLimit-Remaining"),
        "reset": _integer_header(headers, "X-RateLimit-Reset"),
    }


def _rate_limit_message(rate_limit: Dict[str, Optional[int]]) -> str:
    """Build a clear rate-limit message without exposing authentication data."""
    reset = rate_limit.get("reset")
    reset_note = ""
    if reset is not None:
        reset_time = datetime.fromtimestamp(reset, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        reset_note = f" Limit resets at {reset_time}."
    return f"GitHub API rate limit reached.{reset_note} Set GITHUB_TOKEN for higher limits."


def github_get(
    path: str,
    token: Optional[str],
    timeout: float,
) -> Tuple[Optional[object], List[str], int, Dict[str, Optional[int]]]:
    """GET a GitHub API path and return JSON data, errors, status, and rate limit."""
    url = f"{GITHUB_API}{path}"
    try:
        response = requests.get(url, headers=github_headers(token), timeout=timeout)
    except requests.exceptions.Timeout:
        return None, [f"GitHub request timed out after {timeout:g} seconds."], 0, _rate_limit_details({})
    except requests.exceptions.RequestException as exc:
        return None, [f"GitHub network error: {exc}"], 0, _rate_limit_details({})

    rate_limit = _rate_limit_details(response.headers)
    if response.status_code in (403, 429) and rate_limit.get("remaining") == 0:
        return None, [_rate_limit_message(rate_limit)], response.status_code, rate_limit
    if response.status_code == 404:
        return None, ["GitHub resource not found."], response.status_code, rate_limit
    if response.status_code >= 400:
        return None, [f"GitHub API error {response.status_code}: {response.reason}"], response.status_code, rate_limit

    try:
        return response.json(), [], response.status_code, rate_limit
    except ValueError:
        return None, ["GitHub returned malformed JSON."], response.status_code, rate_limit


def detect_repo_tech(language: Optional[str], files: Iterable[str]) -> Tuple[List[str], List[str]]:
    """Infer a repo tech stack and recon notes from metadata and file names."""
    file_set = {item.lower() for item in files}
    tech = set()
    notes = set()

    if language:
        tech.add(language)

    if "package.json" in file_set:
        tech.add("Node.js")
        notes.add("JavaScript/Node project indicators detected")
    if "requirements.txt" in file_set or "pyproject.toml" in file_set or "setup.py" in file_set:
        tech.add("Python")
        notes.add("Python project indicators detected")
    if "cargo.toml" in file_set:
        tech.add("Rust")
        notes.add("Rust project indicators detected")
    if "go.mod" in file_set:
        tech.add("Go")
        notes.add("Go project indicators detected")
    if "dockerfile" in file_set or "docker-compose.yml" in file_set:
        tech.add("Docker")
        notes.add("Docker usage detected")
    if any(item.startswith(".github/workflows/") for item in file_set):
        notes.add("CI/CD workflows detected")
    if ".env.example" in file_set:
        notes.add("Environment example file present")
    if "security.md" in file_set:
        notes.add("Security policy file present")
    if "codeowners" in file_set:
        notes.add("CODEOWNERS file present")
    if any(item in file_set for item in (".github/dependabot.yml", ".github/dependabot.yaml")):
        notes.add("Dependency automation detected")
    if any(item in file_set for item in ("vercel.json", "netlify.toml", "render.yaml", "procfile", "serverless.yml", "serverless.yaml")):
        notes.add("Possible deployment configuration detected")
    if any(item.endswith(".tf") or item.startswith("terraform/") for item in file_set):
        notes.add("Infrastructure-as-code indicators detected")
    if any(item in file_set for item in ("chart.yaml", "kustomization.yaml")):
        notes.add("Kubernetes/Helm indicators detected")
    if any(item in file_set for item in ("next.config.js", "next.config.ts")):
        tech.add("Next.js")
        notes.add("Frontend framework indicators detected")
    if any(item in file_set for item in ("vite.config.js", "vite.config.ts")):
        tech.add("Vite")
        notes.add("Frontend framework indicators detected")
    if any(item in file_set for item in ("requirements.txt", "pyproject.toml", "setup.py", "go.mod", "cargo.toml", "package.json")):
        notes.add("Backend/API indicators may be present; validate manually before making claims")

    return sorted(tech), sorted(notes)


def parse_repo(repo: Dict[str, object], files: Optional[List[str]] = None) -> Dict[str, object]:
    """Normalize a GitHub repository API object for terminal and report output."""
    interesting_files = files or []
    tech_stack, recon_notes = detect_repo_tech(repo.get("language") if isinstance(repo.get("language"), str) else None, interesting_files)
    return {
        "name": repo.get("name") or "",
        "description": repo.get("description") or "",
        "url": repo.get("html_url") or "",
        "stars": repo.get("stargazers_count") or 0,
        "forks": repo.get("forks_count") or 0,
        "language": repo.get("language") or "",
        "default_branch": repo.get("default_branch") or "",
        "updated_at": repo.get("updated_at") or "",
        "archived": bool(repo.get("archived")),
        "private": bool(repo.get("private")),
        "fork": bool(repo.get("fork")),
        "interesting_files": interesting_files,
        "tech_stack": tech_stack,
        "recon_notes": recon_notes,
    }


def _is_interesting_path(path: str) -> bool:
    """Return whether a Git tree path is relevant to lightweight repo recon."""
    normalized = path.strip().lower()
    exact_paths = {item.lower() for item in INTERESTING_FILES}
    if normalized in exact_paths:
        return True
    if normalized.startswith(".github/workflows/") and normalized.endswith((".yml", ".yaml")):
        return True
    if normalized.endswith(".tf"):
        return True
    return normalized.endswith(("/chart.yaml", "/kustomization.yaml"))


def fetch_interesting_files(
    owner: str,
    repo: str,
    branch: str,
    token: Optional[str],
    timeout: float,
) -> Tuple[List[str], List[str], Dict[str, Optional[int]]]:
    """Collect interesting paths with one recursive Git tree request."""
    encoded_branch = quote(branch, safe="")
    data, request_errors, status, rate_limit = github_get(
        f"/repos/{owner}/{repo}/git/trees/{encoded_branch}?recursive=1",
        token,
        timeout,
    )
    if status != 200 or not isinstance(data, dict):
        errors = [f"{repo}: {error}" for error in request_errors]
        return [], errors, rate_limit

    found = []
    tree = data.get("tree")
    if isinstance(tree, list):
        for item in tree:
            if not isinstance(item, dict) or item.get("type") != "blob":
                continue
            path = str(item.get("path") or "")
            if path and _is_interesting_path(path):
                found.append(path)

    errors = []
    if data.get("truncated") is True:
        errors.append(f"{repo}: GitHub tree response was truncated; interesting files may be incomplete.")
    return sorted(set(found)), errors, rate_limit


def fetch_github_recon(
    owner: str,
    repo: Optional[str] = None,
    timeout: float = 10.0,
    max_repos: int = 10,
    token: Optional[str] = None,
) -> Dict[str, object]:
    """Collect lightweight public GitHub repository recon for an owner or repo."""
    cleaned_owner = owner.strip() if owner else ""
    cleaned_repo = repo.strip() if repo else ""
    errors: List[str] = []
    repos: List[Dict[str, object]] = []
    rate_limit: Dict[str, Optional[int]] = _rate_limit_details({})
    token = token if token is not None else os.environ.get("GITHUB_TOKEN")

    if not cleaned_owner:
        return {"owner": owner, "repos": [], "errors": ["GitHub owner is required."], "rate_limit": rate_limit}

    if cleaned_repo:
        data, request_errors, status, rate_limit = github_get(f"/repos/{cleaned_owner}/{cleaned_repo}", token, timeout)
        if status == 404:
            return {
                "owner": cleaned_owner,
                "repo": cleaned_repo,
                "repos": [],
                "errors": [f"GitHub repo not found: {cleaned_owner}/{cleaned_repo}"],
                "rate_limit": rate_limit,
            }
        if request_errors:
            return {
                "owner": cleaned_owner,
                "repo": cleaned_repo,
                "repos": [],
                "errors": request_errors,
                "rate_limit": rate_limit,
            }
        repo_items = [data] if isinstance(data, dict) else []
    else:
        owner_data, owner_errors, owner_status, rate_limit = github_get(f"/users/{cleaned_owner}", token, timeout)
        if owner_status == 404:
            return {
                "owner": cleaned_owner,
                "repos": [],
                "errors": [f"GitHub owner not found: {cleaned_owner}"],
                "rate_limit": rate_limit,
            }
        if owner_errors:
            return {"owner": cleaned_owner, "repos": [], "errors": owner_errors, "rate_limit": rate_limit}

        owner_type = ""
        if isinstance(owner_data, dict):
            owner_type = str(owner_data.get("type") or "")
        path = f"/orgs/{cleaned_owner}/repos" if owner_type == "Organization" else f"/users/{cleaned_owner}/repos"
        data, request_errors, status, rate_limit = github_get(f"{path}?sort=updated&per_page={max_repos}", token, timeout)
        if request_errors:
            return {"owner": cleaned_owner, "repos": [], "errors": request_errors, "rate_limit": rate_limit}
        repo_items = data if isinstance(data, list) else []

    for repo_data in repo_items[:max_repos]:
        if not isinstance(repo_data, dict):
            continue
        name = str(repo_data.get("name") or "")
        branch = str(repo_data.get("default_branch") or "")
        files: List[str] = []
        if name and branch:
            files, file_errors, rate_limit = fetch_interesting_files(cleaned_owner, name, branch, token, timeout)
            errors.extend(file_errors)
        repos.append(parse_repo(repo_data, files))

    return {
        "owner": cleaned_owner,
        "repo": cleaned_repo or None,
        "repos": repos,
        "errors": errors,
        "rate_limit": rate_limit,
    }
