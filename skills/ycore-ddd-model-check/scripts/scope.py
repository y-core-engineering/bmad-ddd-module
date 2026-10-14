#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""scope: which files a domain model check covers, and which Bounded Context each belongs to.

Modes:
  epic   --plans <folder>     every BMad build plan below the folder (Markdown files whose
                              frontmatter has `baseline_revision`), typically an epic's folder
                              beside its tickets.toml; the range runs from the oldest baseline
                              to --to or HEAD
  plan   --plan <file>        one build plan; its baseline to --to or HEAD
  range  --range <a>..<b>     an explicit commit range
  codebase                    every tracked file

Assignment: with --map, the first Markdown table in that file whose header has a "Context"
column and a "Path" or "Module" column; each row maps a path, folder or glob to a context.
A file belongs to the context with the longest matching entry. Without --map, or for files
no entry matches, files land in "unassigned" for the checker to assign by judgment.

Usage:
  scope.py <mode> --repo <git root> [--plans DIR | --plan FILE | --range A..B] [--to REV] [--map FILE]

Output, one JSON object on stdout:
  {"mode", "range": {"from", "to", "to_derived"} | null, "plans": [{"file", "ticket", "status",
   "baseline"}], "mapped": bool, "files": [{"path", "status", "context"}],
   "contexts": {context: [paths]}, "unassigned": [paths], "notes": [...]}
Exit 0, or 2 on a usage, Git or read error (reason on stderr).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*(#.*)?$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip("'\"")
    return fields


def read_plans(paths: list[Path]) -> list[dict[str, str]]:
    plans = []
    for p in paths:
        fm = frontmatter(p)
        if "baseline_revision" in fm:
            plans.append({"file": str(p), "ticket": fm.get("ticket", ""), "status": fm.get("status", ""),
                          "baseline": fm["baseline_revision"]})
    return plans


def oldest(repo: Path, revisions: list[str]) -> str:
    """The revision that is an ancestor of all others; the first one on ties or unrelated history."""
    best = revisions[0]
    for rev in revisions[1:]:
        ok = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", rev, best]).returncode == 0
        if ok:
            best = rev
    return best


def read_map(path: Path) -> list[tuple[str, str]]:
    """Entries of the first table whose header has Context and Path or Module."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("|"):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    for block in blocks:
        header = [c.strip().lower() for c in block[0].strip().strip("|").split("|")]
        if "context" not in header or not ("path" in header or "module" in header):
            continue
        target_col = header.index("path") if "path" in header else header.index("module")
        entries = []
        for line in block[1:]:
            if re.fullmatch(r"[\s|:\-]+", line):
                continue
            cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
            if len(cells) <= max(target_col, header.index("context")):
                continue
            ctx = cells[header.index("context")]
            for part in re.split(r"[,;]\s*", cells[target_col]):
                if part.strip() and ctx:
                    entries.append((part.strip(), ctx))
        return entries
    return []


def match_length(path: str, pattern: str) -> int:
    pattern = pattern.rstrip("/")
    if any(ch in pattern for ch in "*?["):
        return len(pattern) if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern + "/*") else 0
    return len(pattern) if path == pattern or path.startswith(pattern + "/") else 0


def assign(path: str, entries: list[tuple[str, str]]) -> str | None:
    best, length = None, 0
    for pattern, ctx in entries:
        n = match_length(path, pattern)
        if n > length:
            best, length = ctx, n
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["epic", "plan", "range", "codebase"])
    parser.add_argument("--repo", required=True, type=Path, help="root of the Git repository")
    parser.add_argument("--plans", type=Path, help="epic folder holding build plans (mode epic)")
    parser.add_argument("--plan", type=Path, help="one build plan (mode plan)")
    parser.add_argument("--range", dest="rng", help="A..B (mode range)")
    parser.add_argument("--to", help="end of the range instead of HEAD")
    parser.add_argument("--map", type=Path, help="Markdown file with a Context/Path table")
    args = parser.parse_args()

    out: dict = {"mode": args.mode, "range": None, "plans": [], "mapped": False, "files": [],
                 "contexts": {}, "unassigned": [], "notes": []}
    try:
        repo = args.repo.resolve()
        files: list[tuple[str, str]] = []
        start = end = None
        if args.mode in ("epic", "plan"):
            if args.mode == "epic":
                if not args.plans or not args.plans.is_dir():
                    raise ValueError("mode epic needs --plans <folder>")
                plans = read_plans(sorted(args.plans.rglob("*.md")))
            else:
                if not args.plan or not args.plan.is_file():
                    raise ValueError("mode plan needs --plan <file>")
                plans = read_plans([args.plan])
            out["plans"] = plans
            usable = [p["baseline"] for p in plans if p["baseline"] and p["baseline"] != "NO_VCS"]
            for p in plans:
                if not p["baseline"] or p["baseline"] == "NO_VCS":
                    out["notes"].append(f"plan {p['file']} has no baseline_revision; its changes cannot be located")
            if not usable:
                raise ValueError("no build plan with a baseline_revision found")
            start = oldest(repo, usable)
        elif args.mode == "range":
            if not args.rng or ".." not in args.rng:
                raise ValueError("mode range needs --range A..B")
            start, end = args.rng.split("..", 1)
        if args.mode == "codebase":
            files = [(f, "") for f in git(repo, "ls-files").splitlines() if f]
        else:
            end = end or args.to or "HEAD"
            out["range"] = {"from": start, "to": end, "to_derived": args.mode in ("epic", "plan") and not args.to}
            for line in git(repo, "diff", "--name-status", "-M", f"{start}..{end}").splitlines():
                parts = line.split("\t")
                status = parts[0][0]
                files.append((parts[-1], status))
        entries: list[tuple[str, str]] = []
        if args.map:
            if not args.map.is_file():
                raise ValueError(f"map not found: {args.map}")
            entries = read_map(args.map)
            out["mapped"] = bool(entries)
            if not entries:
                out["notes"].append(f"{args.map} has no table with a Context and a Path or Module column")
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"scope: {exc}", file=sys.stderr)
        return 2

    for path, status in files:
        ctx = assign(path, entries) if entries else None
        out["files"].append({"path": path, "status": status, "context": ctx})
        if ctx:
            out["contexts"].setdefault(ctx, []).append(path)
        else:
            out["unassigned"].append(path)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
