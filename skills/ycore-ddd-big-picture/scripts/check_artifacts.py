#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_artifacts: structure check of the Big-Picture Event Storming artifacts.

Verifies what later readers parse: context-map.md with its Contexts and Edges tables
and a Mermaid diagram, ubiquitous-language.md and event-storming.md with one
`## BC## <Context>` section per context, IDs and names identical across the files,
edge endpoints that exist, patterns from the fixed list, trust boundary `no` or
`yes: <which>`. Whether a boundary or a protection need is sound stays with the reader.

Usage:
  check_artifacts.py --folder <domain_model_folder>

Output, one JSON object on stdout:
  {"ok": bool, "files_missing": [...], "sections_missing": [{"file", "section"}],
   "columns_missing": [{"file", "table", "column"}],
   "bad_cells": [{"file", "row", "column", "value", "rule"}],
   "cross_refs": [{"file", "problem"}]}
Exit 0 when no gaps, 1 when gaps were found, 2 when the folder cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FILES = ["context-map.md", "ubiquitous-language.md", "event-storming.md"]
CONTEXT_COLUMNS = ["ID", "Context", "Subdomain", "Responsibility", "Most sensitive data", "Protection need"]
EDGE_COLUMNS = ["ID", "From", "To", "Pattern", "What flows", "Trust boundary"]
GLOSSARY_COLUMNS = ["Term", "Definition", "Conflicts"]
SUBDOMAINS = {"Core", "Supporting", "Generic"}
PATTERNS = {"Partnership", "Shared Kernel", "Customer/Supplier", "Conformist", "Anti-Corruption Layer",
            "Open Host Service", "Published Language", "Separate Ways"}
BC_HEADING = re.compile(r"^(BC\d+)\s+(.+?)\s*$")


def split_sections(text: str) -> tuple[dict[str, str], list[str]]:
    """Sections by `## ` heading, ignoring headings inside fenced blocks; also the repeated titles."""
    sections: dict[str, str] = {}
    repeated: list[str] = []
    current, lines, fenced = None, [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(lines)
            current, lines = m.group(1), []
            if current in sections:
                repeated.append(current)
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines)
    return sections, repeated


def cells(line: str) -> list[str]:
    inner = line.strip().removeprefix("|").removesuffix("|")
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]


def parse_table(body: str) -> tuple[list[str], list[dict[str, str]]]:
    rows = [line for line in body.splitlines() if line.strip().startswith("|")]
    if not rows:
        return [], []
    header = cells(rows[0])
    data = []
    for r in rows[1:]:
        if re.fullmatch(r"[\s|:\-]+", r):
            continue
        values = cells(r)
        data.append({h: (values[i] if i < len(values) else "") for i, h in enumerate(header)})
    return header, data


def bc_sections(sections: dict[str, str]) -> dict[str, tuple[str, str]]:
    found = {}
    for title, body in sections.items():
        m = BC_HEADING.match(title)
        if m:
            found[m.group(1)] = (m.group(2), body)
    return found


def check(folder: Path) -> dict:
    r = {"files_missing": [], "sections_missing": [], "columns_missing": [], "bad_cells": [], "cross_refs": []}
    texts = {}
    for name in FILES:
        path = folder / name
        if path.is_file():
            texts[name] = path.read_text(encoding="utf-8")
        else:
            r["files_missing"].append(name)

    def need_columns(file, table, header, expected):
        for col in expected:
            if col not in header:
                r["columns_missing"].append({"file": file, "table": table, "column": col})

    def bad(file, row, column, value, rule):
        r["bad_cells"].append({"file": file, "row": row, "column": column, "value": value, "rule": rule})

    contexts: dict[str, str] = {}
    if "context-map.md" in texts:
        f = "context-map.md"
        sections, repeated = split_sections(texts[f])
        for title in repeated:
            r["cross_refs"].append({"file": f, "problem": f"section '{title}' appears more than once"})
        for sec in ("Contexts", "Edges", "Diagram"):
            if sec not in sections:
                r["sections_missing"].append({"file": f, "section": sec})
        header, rows = parse_table(sections.get("Contexts", ""))
        if "Contexts" in sections:
            need_columns(f, "Contexts", header, CONTEXT_COLUMNS)
        for i, row in enumerate(rows, start=1):
            cid, sub = row.get("ID", ""), row.get("Subdomain", "")
            if re.fullmatch(r"BC\d+", cid):
                if sub not in SUBDOMAINS:
                    bad(f, i, "Subdomain", sub, "Core, Supporting or Generic for a BC row")
                for col in ("Context", "Responsibility", "Most sensitive data", "Protection need"):
                    if not row.get(col):
                        bad(f, i, col, "", "empty")
            elif re.fullmatch(r"X\d+", cid):
                if sub != "External":
                    bad(f, i, "Subdomain", sub, "External for an X row")
                if not row.get("Context"):
                    bad(f, i, "Context", "", "empty")
            else:
                bad(f, i, "ID", cid, "BC## or X##")
                continue
            if cid in contexts:
                bad(f, i, "ID", cid, "repeated")
            contexts[cid] = row.get("Context", "")
        names = [n for n in contexts.values() if n]
        for name in sorted({n for n in names if names.count(n) > 1}):
            r["cross_refs"].append({"file": f, "problem": f"context name '{name}' used for more than one ID"})
        if not any(k.startswith("BC") for k in contexts):
            r["cross_refs"].append({"file": f, "problem": "Contexts table has no BC row"})

        header, rows = parse_table(sections.get("Edges", ""))
        if "Edges" in sections:
            need_columns(f, "Edges", header, EDGE_COLUMNS)
        seen = set()
        for i, row in enumerate(rows, start=1):
            eid = row.get("ID", "")
            if not re.fullmatch(r"K-\d+", eid):
                bad(f, i, "ID", eid, "K-<nn>")
            elif eid in seen:
                bad(f, i, "ID", eid, "repeated")
            seen.add(eid)
            if row.get("From") and row.get("From") == row.get("To"):
                bad(f, i, "To", row.get("To", ""), "differs from From")
            for col in ("From", "To"):
                if row.get(col, "") not in contexts:
                    bad(f, i, col, row.get(col, ""), "an ID from the Contexts table")
            parts = [p.strip() for p in row.get("Pattern", "").split(" / ")]
            if len(parts) > 2 or any(p not in PATTERNS for p in parts):
                bad(f, i, "Pattern", row.get("Pattern", ""), "one or two of the fixed patterns, joined by ' / '")
            trust = row.get("Trust boundary", "")
            if trust != "no" and not re.fullmatch(r"yes:\s*\S.*", trust):
                bad(f, i, "Trust boundary", trust, "no, or yes: <which>")
            if not row.get("What flows"):
                bad(f, i, "What flows", "", "empty")
        if "Diagram" in sections and "```mermaid" not in sections["Diagram"]:
            r["cross_refs"].append({"file": f, "problem": "Diagram section has no mermaid block"})

    bcs = {k: v for k, v in contexts.items() if k.startswith("BC")}
    for f in ("ubiquitous-language.md", "event-storming.md"):
        if f not in texts:
            continue
        sections, repeated = split_sections(texts[f])
        for title in repeated:
            r["cross_refs"].append({"file": f, "problem": f"section '{title}' appears more than once"})
        found = bc_sections(sections)
        for cid, name in bcs.items():
            if cid not in found:
                r["sections_missing"].append({"file": f, "section": f"{cid} {name}"})
            elif found[cid][0] != name:
                r["cross_refs"].append({"file": f, "problem": f"{cid} is '{found[cid][0]}' here, '{name}' in context-map.md"})
        for cid in found:
            if bcs and cid not in bcs:
                r["cross_refs"].append({"file": f, "problem": f"{cid} has no row in context-map.md"})
        if f == "ubiquitous-language.md":
            for cid, (_, body) in found.items():
                header, _rows = parse_table(body)
                need_columns(f, cid, header, GLOSSARY_COLUMNS)
        elif "```mermaid" not in texts[f]:
            r["cross_refs"].append({"file": f, "problem": "no mermaid event flow"})

    r["ok"] = not any(r[k] for k in ("files_missing", "sections_missing", "columns_missing", "bad_cells", "cross_refs"))
    return r


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, type=Path, help="the domain model folder")
    args = parser.parse_args()
    if not args.folder.is_dir():
        print(json.dumps({"ok": False, "error": f"folder not found: {args.folder}"}))
        return 2
    try:
        result = check(args.folder)
    except (OSError, UnicodeDecodeError) as exc:
        print(json.dumps({"ok": False, "error": f"unreadable: {exc}"}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
