#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_report: structure check and tally of a domain model review report.

Reads the report written by references/check.md and verifies what has one right
answer: the required sections exist, the findings table has its columns, every
finding has ID, check 1-5, severity, both locations and a boundary mark that fits
its check, every code location resolves to a file and line range under the project
root, and every check 1-5 has findings or is named under "Checked and sound" or
"Not checked". Whether a counterpart is the right one stays with the reader.

Usage:
  check_report.py --report <report.md> --project-root <dir> [--require-decisions]

With --require-decisions it also checks the "## Decisions" table that the skill adds after
the user has decided: every high and medium finding has a row whose Decision is "fix in
code", "update model" or "accept deviation" and whose Follow-up is not empty, and the
report's frontmatter says "status: final".

Output, one JSON object on stdout:
  {"ok": bool, "sections_missing": [...], "columns_missing": [...],
   "findings": [{"id", "row", "problems": [...]}, ...]   (only rows with problems),
   "checks_unaccounted": [int, ...], "decisions_missing": [ids] (with --require-decisions),
   "tally": {"total", "by_check": {"1": n, ...}, "by_severity": {...}, "boundary": n}}
Exit 0 when no gaps, 1 when gaps were found, 2 when the report cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["Frame", "Findings", "Checked and sound", "Not assignable", "Not checked"]
COLUMNS = ["ID", "Check", "Severity", "Context", "Code location", "Model counterpart",
           "Boundary", "Finding", "Direction or question"]
SEVERITIES = ("high", "medium", "low")
DECISIONS = ("fix in code", "update model", "accept deviation", "left open")
BOUNDARY_CHECKS = {2, 4}
LOCATION = re.compile(r"^`?(?P<path>[^`:]+?):(?P<start>\d+)(?:-(?P<end>\d+))?`?$")
CHECK_LABEL = re.compile(r"^\s*(?:[-*]\s*|#+\s*)?check\s*([1-5])\b", re.IGNORECASE | re.MULTILINE)


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(lines)
            current, lines = m.group(1), []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines)
    return sections


def cells(line: str) -> list[str]:
    inner = line.strip().removeprefix("|").removesuffix("|")
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]


def parse_table(body: str) -> tuple[list[str], list[list[str]]]:
    rows = [line for line in body.splitlines() if line.strip().startswith("|")]
    if not rows:
        return [], []
    header = cells(rows[0])
    data = [cells(r) for r in rows[1:] if not re.fullmatch(r"[\s|:\-]+", r)]
    return header, data


def location_problem(value: str, root: Path) -> str | None:
    m = LOCATION.match(value)
    if not m:
        return f"code location '{value}' is not path:line or path:start-end"
    path = (root / m.group("path").strip()).resolve()
    if not path.is_file():
        return f"code location file not found: {m.group('path').strip()}"
    try:
        count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError as exc:
        return f"code location unreadable: {exc}"
    start = int(m.group("start"))
    end = int(m.group("end") or start)
    if start < 1 or end < start or end > count:
        return f"code location lines {start}-{end} outside file of {count} lines"
    return None


def check(report: Path, root: Path, require_decisions: bool = False) -> dict:
    text = report.read_text(encoding="utf-8")
    sections = split_sections(text)
    result: dict = {
        "sections_missing": [s for s in REQUIRED_SECTIONS if s not in sections],
        "columns_missing": [],
        "findings": [],
        "checks_unaccounted": [],
    }
    tally = {"total": 0, "by_check": {str(n): 0 for n in range(1, 6)},
             "by_severity": {s: 0 for s in SEVERITIES}, "boundary": 0}

    header, rows = parse_table(sections.get("Findings", ""))
    if rows or header:
        result["columns_missing"] = [c for c in COLUMNS if c not in header]
    col = {name: header.index(name) for name in COLUMNS if name in header}
    seen_ids: set[str] = set()
    checks_found: set[int] = set()

    for i, row in enumerate(rows, start=1):
        get = lambda name: row[col[name]] if name in col and col[name] < len(row) else ""
        problems = []
        if len(row) != len(header):
            problems.append(f"row has {len(row)} cells, header {len(header)}")
        fid = get("ID")
        if not re.fullmatch(r"FM-\d+", fid):
            problems.append(f"ID '{fid}' is not FM-<n>")
        elif fid in seen_ids:
            problems.append(f"ID {fid} repeated")
        seen_ids.add(fid)

        chk = get("Check")
        n = int(chk) if chk.isdigit() and 1 <= int(chk) <= 5 else None
        if n is None:
            problems.append(f"check '{chk}' is not 1-5")
        else:
            checks_found.add(n)
            tally["by_check"][str(n)] += 1

        sev = get("Severity").lower()
        if sev in SEVERITIES:
            tally["by_severity"][sev] += 1
        else:
            problems.append(f"severity '{get('Severity')}' is not high, medium or low")

        boundary = get("Boundary").lower()
        if boundary not in ("yes", "no"):
            problems.append(f"boundary '{get('Boundary')}' is not yes or no")
        elif n is not None and (boundary == "yes") != (n in BOUNDARY_CHECKS):
            problems.append(f"boundary '{boundary}' does not fit check {n}")
        if boundary == "yes":
            tally["boundary"] += 1

        for name in ("Context", "Model counterpart", "Finding", "Direction or question"):
            if not get(name):
                problems.append(f"{name.lower()} empty")
        loc = get("Code location")
        if loc in ("", "-", "—") and n == 5:
            pass  # model element without counterpart in the code
        elif not loc:
            problems.append("code location empty")
        else:
            problem = location_problem(loc, root)
            if problem:
                problems.append(problem)

        tally["total"] += 1
        if problems:
            result["findings"].append({"id": fid, "row": i, "problems": problems})

    mentioned = {int(m) for key in ("Checked and sound", "Not checked")
                 for m in CHECK_LABEL.findall(sections.get(key, ""))}
    result["checks_unaccounted"] = [n for n in range(1, 6)
                                    if n not in checks_found and n not in mentioned]
    result["tally"] = tally
    if require_decisions:
        weighty = [r[col["ID"]] for r in rows if "ID" in col and "Severity" in col
                   and col["Severity"] < len(r) and r[col["Severity"]].lower() in ("high", "medium")]
        d_header, d_rows = parse_table(sections.get("Decisions", ""))
        decided = {}
        for r in d_rows:
            cell = dict(zip(d_header, r))
            if cell.get("Decision", "").lower() in DECISIONS and cell.get("Follow-up"):
                decided[cell.get("Finding", "")] = cell["Decision"].lower()
        result["decisions_missing"] = [fid for fid in weighty if decided.get(fid) in (None, "left open")]
        status = re.search(r"^status:\s*(\w+)", text, re.MULTILINE)
        if not status or status.group(1) != "final":
            result["decisions_missing"].append("status: final")
    result["ok"] = not (result["sections_missing"] or result["columns_missing"]
                        or result["findings"] or result["checks_unaccounted"]
                        or result.get("decisions_missing"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", required=True, type=Path, help="report markdown file")
    parser.add_argument("--project-root", required=True, type=Path,
                        help="root that code locations are relative to")
    parser.add_argument("--require-decisions", action="store_true",
                        help="also require a decision for every high and medium finding")
    args = parser.parse_args()
    if not args.report.is_file():
        print(json.dumps({"ok": False, "error": f"report not found: {args.report}"}))
        return 2
    try:
        result = check(args.report, args.project_root.resolve(), args.require_decisions)
    except (OSError, UnicodeDecodeError) as exc:
        print(json.dumps({"ok": False, "error": f"report unreadable: {exc}"}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
