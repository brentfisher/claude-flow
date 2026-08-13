#!/usr/bin/env python3
"""Deterministic facts pass over a target repo: file tree, language mix,
manifest/framework detection, git history stats. No LLM calls — pure
scripting, output is JSON on stdout for the calling skill to read.

Usage: crawl_repo.py <target-repo-path> [--top-n N]
"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "target",
    "venv", ".venv", "__pycache__", ".next", ".turbo", "coverage",
}

FRAMEWORK_MANIFESTS = {
    "package.json": "node",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "pom.xml": "java-maven",
    "build.gradle": "java-gradle",
    "Gemfile": "ruby",
    "composer.json": "php",
}


def run(cmd, cwd):
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except Exception:
        return ""


def is_git_repo(path):
    return run(["git", "rev-parse", "--is-inside-work-tree"], path) == "true"


def list_tracked_files(path):
    out = run(["git", "ls-files"], path)
    if out:
        return [Path(p) for p in out.splitlines()]
    files = []
    for root, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for name in names:
            files.append(Path(os.path.relpath(os.path.join(root, name), path)))
    return files


def git_facts(path):
    if not is_git_repo(path):
        return {}
    return {
        "remote": run(["git", "remote", "get-url", "origin"], path) or None,
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"], path) or None,
        "head_commit": run(["git", "rev-parse", "HEAD"], path) or None,
        "commit_count": run(["git", "rev-list", "--count", "HEAD"], path) or "0",
        "recent_log": run(
            ["git", "log", "-20", "--pretty=format:%h %ad %s", "--date=short"], path
        ),
    }


def most_changed_files(path, top_n):
    out = run(["git", "log", "--pretty=format:", "--name-only", "-500"], path)
    if not out:
        return []
    counts = Counter(line for line in out.splitlines() if line.strip())
    return [{"path": p, "changes": n} for p, n in counts.most_common(top_n)]


def language_mix(files):
    return dict(Counter(f.suffix for f in files if f.suffix).most_common(30))


def detect_manifests_and_frameworks(path, files):
    names = {f.name for f in files}
    found = [m for m in FRAMEWORK_MANIFESTS if m in names]
    frameworks = sorted({FRAMEWORK_MANIFESTS[m] for m in found})
    return found, frameworks


def largest_files(path, files, top_n):
    sized = []
    for f in files:
        full = Path(path) / f
        try:
            lines = sum(1 for _ in open(full, "r", errors="ignore"))
            sized.append({"path": str(f), "lines": lines})
        except (OSError, UnicodeDecodeError):
            continue
    sized.sort(key=lambda x: x["lines"], reverse=True)
    return sized[:top_n]


def main():
    if len(sys.argv) < 2:
        print("usage: crawl_repo.py <target-repo-path> [--top-n N]", file=sys.stderr)
        sys.exit(1)
    target = str(Path(sys.argv[1]).resolve())
    top_n = 20
    if "--top-n" in sys.argv:
        top_n = int(sys.argv[sys.argv.index("--top-n") + 1])

    files = list_tracked_files(target)
    manifests, frameworks = detect_manifests_and_frameworks(target, files)

    result = {
        "target_path": target,
        "total_files": len(files),
        "git": git_facts(target),
        "languages_by_extension": language_mix(files),
        "manifests_found": manifests,
        "frameworks_detected": frameworks,
        "largest_files": largest_files(target, files, top_n),
        "most_changed_files": most_changed_files(target, top_n),
        "top_level_entries": sorted(
            {f.parts[0] for f in files if f.parts}
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
