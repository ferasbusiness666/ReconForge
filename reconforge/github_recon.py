"""GitHub public API recon helpers."""

from __future__ import annotations

import os
from typing import Dict, Iterable, List, Optional, Tuple

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


def github_get(path: str, token: Optional[str], timeout: float) -> Tuple[Optional[object], List[str], int]:
    """GET a GitHub API path and return JSON data, errors, and status code."""
    url = f"{GITHUB_API}{path}"
    try:
        response = requests.get(url, headers=github_headers(token), timeout=timeout)
    except requests.exceptions.Timeout:
        return None, [f"GitHub request timed out after {timeout:g} seconds."], 0
    except requests.exceptions.RequestException as exc:
        return None, [f"GitHub network error: {exc}"], 0

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        return None, ["GitHub API rate limit reached. Set GITHUB_TOKEN for higher limits."], response.status_code
    if response.status_code == 404:
        return None, ["GitHub resource not found."], response.status_code
    if response.status_code >= 400:
        return None, [f"GitHub API error {response.status_code}: {response.reason}"], response.status_code

    try:
        return response.json(), [], response.status_code
    except ValueError:
        return None, ["GitHub returned malformed JSON."], response.status_code


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


def fetch_interesting_files(owner: str, repo: str, branch: str, token: Optional[str], timeout: float) -> Tuple[List[str], List[str]]:
    """Check for a small allowlist of interesting files in a repository."""
    found: List[str] = []
    errors: List[str] = []

    for path in INTERESTING_FILES:
        data, request_errors, status = github_get(f"/repos/{owner}/{repo}/contents/{path}?ref={branch}", token, timeout)
        if status == 200 and data is not None:
            found.append(path)
        elif status not in (0, 404):
            errors.extend([f"{repo}: {error}" for error in request_errors])

    workflows, workflow_errors, status = github_get(f"/repos/{owner}/{repo}/contents/.github/workflows?ref={branch}", token, timeout)
    if status == 200 and isinstance(workflows, list):
        for item in workflows:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "")
            path = str(item.get("path") or "")
            if name.endswith((".yml", ".yaml")) and path:
                found.append(path)
    elif status not in (0, 404):
        errors.extend([f"{repo}: {error}" for error in workflow_errors])

    return sorted(set(found)), errors


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
    token = token if token is not None else os.environ.get("GITHUB_TOKEN")

    if not cleaned_owner:
        return {"owner": owner, "repos": [], "errors": ["GitHub owner is required."]}

    if cleaned_repo:
        data, request_errors, status = github_get(f"/repos/{cleaned_owner}/{cleaned_repo}", token, timeout)
        if status == 404:
            return {"owner": cleaned_owner, "repo": cleaned_repo, "repos": [], "errors": [f"GitHub repo not found: {cleaned_owner}/{cleaned_repo}"]}
        if request_errors:
            return {"owner": cleaned_owner, "repo": cleaned_repo, "repos": [], "errors": request_errors}
        repo_items = [data] if isinstance(data, dict) else []
    else:
        owner_data, owner_errors, owner_status = github_get(f"/users/{cleaned_owner}", token, timeout)
        if owner_status == 404:
            return {"owner": cleaned_owner, "repos": [], "errors": [f"GitHub owner not found: {cleaned_owner}"]}
        if owner_errors:
            return {"owner": cleaned_owner, "repos": [], "errors": owner_errors}

        owner_type = ""
        if isinstance(owner_data, dict):
            owner_type = str(owner_data.get("type") or "")
        path = f"/orgs/{cleaned_owner}/repos" if owner_type == "Organization" else f"/users/{cleaned_owner}/repos"
        data, request_errors, status = github_get(f"{path}?sort=updated&per_page={max_repos}", token, timeout)
        if request_errors:
            return {"owner": cleaned_owner, "repos": [], "errors": request_errors}
        repo_items = data if isinstance(data, list) else []

    for repo_data in repo_items[:max_repos]:
        if not isinstance(repo_data, dict):
            continue
        name = str(repo_data.get("name") or "")
        branch = str(repo_data.get("default_branch") or "")
        files: List[str] = []
        if name and branch:
            files, file_errors = fetch_interesting_files(cleaned_owner, name, branch, token, timeout)
            errors.extend(file_errors)
        repos.append(parse_repo(repo_data, files))

    return {"owner": cleaned_owner, "repo": cleaned_repo or None, "repos": repos, "errors": errors}
