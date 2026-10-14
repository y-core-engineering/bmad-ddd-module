#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_design: structure check and run state of Design-Level design.md files.

Check mode verifies what later readers parse in each design.md: title and depth
line, the sections a full or lean design needs, table columns, ID formats with the
context prefix, fixed cell values, and cross-references inside the file (Commands
name a defined Aggregate and produce Events listed in the file, every Event is
produced by a Command and owned by an Aggregate, Policies react to an Event of the
file, abuse cases name an existing defence). With design-level-catalog.md it also
validates the catalog and compares each design with its row (depth, name, Events).
A context counts as done when its design passes and its board.md says done; for a
lean context that line is written on the user's confirmation.
Whether an invariant is right stays with the reader.

Status mode reports the run state per catalog context and the next target, so the
skill routes on facts rather than on a reading of the files.

Usage:
  check_design.py --folder <domain_model_folder> [--context <bc##-name>]
  check_design.py --folder <domain_model_folder> --status

Output, one JSON object on stdout.
  check:  {"ok", "catalog_problems": [...], "contexts": [{"context", "ok", "problems": [...]}], "missing": [...]}
  status: {"catalog": bool, "catalog_draft": bool, "catalog_problems", "catalog_stale": [...], "big_picture_done": bool,
           "contexts": [{"bc", "context", "folder", "depth", "order", "board_status",
                         "last_round_folder", "design_ok", "done"}], "next_target": folder|null, "all_done": bool}
Exit 0 when no gaps (check) or always after a readable status, 1 when gaps were found,
2 when the folder cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FOLDER = re.compile(r"^(bc\d+)-[a-z0-9]+(?:-[a-z0-9]+)*$")
TABLES = {
    "Commands": ["ID", "Command", "Actor", "May", "Aggregate", "Events"],
    "Events": ["ID", "Event", "Aggregate"],
    "Policies": ["ID", "Whenever", "Then"],
    "Read Models": ["ID", "Read Model", "Serves", "Content"],
    "External Systems and ACLs": ["ID", "System", "ACL translates", "Kept out"],
    "Abuse cases": ["ID", "Abuse case", "STRIDE", "Prevented by", "Protection need"],
    "Hotspots": ["ID", "Question", "Status", "Decision"],
}
INVARIANT_COLUMNS = ["ID", "Invariant", "Security", "Source"]
CATALOG_COLUMNS = ["BC", "Context", "Folder", "Subdomain", "MVP", "Depth", "Order", "Events",
                   "Aggregate candidates", "Hotspots", "External systems"]
FULL_SECTIONS = ["Aggregates", *TABLES, "Flow", "Implementation order"]
LEAN_SECTIONS = ["Why lean", "Aggregates", "Commands", "External Systems and ACLs", "Hotspots"]
ID_LIST = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")


def split_sections(text: str, level: str = "##") -> tuple[dict[str, str], list[str]]:
    sections: dict[str, str] = {}
    repeated: list[str] = []
    current, lines, fenced = None, [], False
    heading = re.compile(rf"^{level}\s+(.+?)\s*$")
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else heading.match(line)
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


def clean_folder(value: str) -> str:
    return value.strip().strip("`/ ")


def read_catalog(folder: Path) -> tuple[list[dict[str, str]] | None, list[str]]:
    """Catalog rows and the problems of the catalog itself; None when there is no catalog."""
    path = folder / "design-level-catalog.md"
    if not path.is_file():
        return None, []
    sections, _ = split_sections(path.read_text(encoding="utf-8"))
    problems = []
    if "Contexts" not in sections:
        return [], ["catalog has no '## Contexts' section"]
    header, rows = parse_table(sections["Contexts"])
    problems += [f"catalog lacks column '{c}'" for c in CATALOG_COLUMNS if c not in header]
    if not rows:
        problems.append("catalog has no context rows")
    known = context_map_ids(folder)
    for row in rows:
        bc = row.get("BC", "") or "<no BC>"
        row["Folder"] = clean_folder(row.get("Folder", ""))
        if not row["Folder"]:
            problems.append(f"catalog row {bc} has no Folder")
        elif not FOLDER.match(row["Folder"]) or FOLDER.match(row["Folder"]).group(1).upper() != bc:
            problems.append(f"catalog row {bc} Folder '{row['Folder']}' is not {bc.lower()}-<ascii-kebab-name>")
        depth, order = row.get("Depth", ""), row.get("Order", "")
        if depth not in ("full", "lean"):
            problems.append(f"catalog row {bc} Depth '{depth}' is not full or lean")
        elif depth == "full" and not order.isdigit():
            problems.append(f"catalog row {bc} is full but Order '{order}' is not a number")
        elif depth == "lean" and order != "-":
            problems.append(f"catalog row {bc} is lean but Order is '{order}', not '-'")
        if known is not None and bc not in known:
            problems.append(f"catalog row {bc} has no row in context-map.md")
    return rows, problems


def context_map_ids(folder: Path) -> dict[str, str] | None:
    path = folder / "context-map.md"
    if not path.is_file():
        return None
    sections, _ = split_sections(path.read_text(encoding="utf-8"))
    _, rows = parse_table(sections.get("Contexts", ""))
    return {r.get("ID", ""): r.get("Context", "") for r in rows if re.fullmatch(r"BC\d+", r.get("ID", ""))}


def id_tokens(value: str) -> list[str]:
    return ID_LIST.findall(value)


def check_context(folder: Path, name: str, row: dict[str, str] | None = None) -> list[str]:
    problems: list[str] = []
    name = clean_folder(name)
    m = FOLDER.match(name)
    if not m:
        return [f"folder '{name}' is not bc##-<ascii-kebab-name>"]
    bc = m.group(1).upper()
    path = folder / name / "design.md"
    if not path.is_file():
        return ["design.md missing"]
    text = path.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.strip()]
    title = re.match(rf"^#\s+{bc}\s+(.+?)\s*·\s*Design\s*$", lines[0]) if lines else None
    if not title:
        problems.append(f"first line is not '# {bc} <Context> · Design'")
    depth_m = re.match(r"^Depth:\s*(full|lean)\s*$", lines[1]) if len(lines) > 1 else None
    if not depth_m:
        problems.append("second line is not 'Depth: full' or 'Depth: lean'")
    depth = depth_m.group(1) if depth_m else "full"
    if row:
        if row.get("Depth") in ("full", "lean") and row["Depth"] != depth:
            problems.append(f"Depth '{depth}' differs from the catalog's '{row['Depth']}'")
        if title and row.get("Context") and title.group(1) != row["Context"]:
            problems.append(f"title names '{title.group(1)}', the catalog '{row['Context']}'")

    sections, repeated = split_sections(text)
    problems += [f"section '{t}' appears more than once" for t in repeated]
    for sec in FULL_SECTIONS if depth == "full" else LEAN_SECTIONS:
        if sec not in sections:
            problems.append(f"section '{sec}' missing")

    ids: list[str] = []
    aggregates: set[str] = set()
    invariants: set[str] = set()
    for heading, body in split_sections(sections.get("Aggregates", ""), "###")[0].items():
        am = re.match(rf"^({bc}-AGG\d+)\s+\S", heading)
        if not am:
            problems.append(f"aggregate heading '{heading}' is not '{bc}-AGG## <Name>'")
            continue
        agg = am.group(1)
        aggregates.add(agg)
        ids.append(agg)
        for label in ("Root:", "Entities:", "Value Objects:"):
            if not re.search(rf"^{label}", body, re.MULTILINE):
                problems.append(f"{agg} has no '{label}' line")
        header, rows = parse_table(body)
        missing = [c for c in INVARIANT_COLUMNS if c not in header]
        if header and missing:
            problems.append(f"{agg} invariants table lacks {', '.join(missing)}")
        if depth == "full" and not rows:
            problems.append(f"{agg} has no invariant")
        for r in rows:
            iid = r.get("ID", "")
            ids.append(iid)
            invariants.add(iid)
            if not re.fullmatch(rf"{bc}-INV\d+", iid):
                problems.append(f"invariant ID '{iid}' is not {bc}-INV##")
            if r.get("Security") not in ("yes", "no"):
                problems.append(f"{iid} Security '{r.get('Security')}' is not yes or no")
            if not r.get("Source"):
                problems.append(f"{iid} has no source")
    if "Aggregates" in sections and not aggregates:
        problems.append("no aggregate under Aggregates")

    tables: dict[str, list[dict[str, str]]] = {}
    for sec, columns in TABLES.items():
        if sec not in sections:
            continue
        header, rows = parse_table(sections[sec])
        missing = [c for c in columns if c not in header]
        if missing:
            problems.append(f"{sec} table lacks {', '.join(missing)}")
            continue
        tables[sec] = rows
        if depth == "full" and sec in ("Commands", "Events", "Abuse cases") and not rows:
            problems.append(f"{sec} table has no row")

    patterns = {
        "Commands": rf"{bc}-C\d+", "Events": rf"E\d+|{bc}-E\d+", "Policies": rf"{bc}-P\d+",
        "Read Models": rf"{bc}-R\d+", "External Systems and ACLs": r"X\d+",
        "Abuse cases": rf"{bc}-M\d+", "Hotspots": rf"H\d+|{bc}-H\d+",
    }
    for sec, rows in tables.items():
        for r in rows:
            rid = r.get("ID", "")
            ids.append(rid)
            if not re.fullmatch(patterns[sec], rid):
                problems.append(f"{sec} ID '{rid}' does not match {patterns[sec]}")

    events = {r["ID"] for r in tables.get("Events", [])}
    commands = {r["ID"] for r in tables.get("Commands", [])}
    hotspots = {r["ID"] for r in tables.get("Hotspots", [])}
    produced: set[str] = set()
    for r in tables.get("Commands", []):
        rid = r["ID"]
        if not r["May"]:
            problems.append(f"{rid} has no May")
        if r["Aggregate"] not in aggregates:
            problems.append(f"{rid} names aggregate '{r['Aggregate']}' not defined here")
        for e in id_tokens(r["Events"]):
            produced.add(e)
            if "Events" in tables and e not in events:
                problems.append(f"{rid} produces {e}, which is not in Events")
    for r in tables.get("Events", []):
        if r["Aggregate"] not in aggregates:
            problems.append(f"{r['ID']} names aggregate '{r['Aggregate']}' not defined here")
        if "Commands" in tables and r["ID"] not in produced:
            problems.append(f"{r['ID']} is produced by no Command")
    for r in tables.get("Policies", []):
        if r["Whenever"] not in events:
            problems.append(f"{r['ID']} reacts to '{r['Whenever']}', not an Event of this file")
        then = r["Then"]
        if not re.fullmatch(r"BC\d+-C\d+", then):
            problems.append(f"{r['ID']} Then '{then}' is not a Command ID")
        elif then.startswith(f"{bc}-") and then not in commands:
            problems.append(f"{r['ID']} Then {then} is not in Commands")
    for r in tables.get("Abuse cases", []):
        letters = re.sub(r"[\s,]", "", r["STRIDE"])
        if not letters or any(ch not in "STRIDE" for ch in letters) or len(set(letters)) != len(letters):
            problems.append(f"{r['ID']} STRIDE '{r['STRIDE']}' is not distinct letters of S T R I D E")
        defences = [t for t in id_tokens(r["Prevented by"]) if t in invariants | commands | hotspots]
        if not defences:
            problems.append(f"{r['ID']} names no invariant, Command or Hotspot of this file as defence")
    for r in tables.get("Hotspots", []):
        if r["Status"] not in ("decided", "moot", "deferred"):
            problems.append(f"{r['ID']} status '{r['Status']}' is not decided, moot or deferred")
        if not r["Decision"]:
            problems.append(f"{r['ID']} has no decision")
    if row and depth == "full" and "Events" in tables:
        for e in id_tokens(row.get("Events", "")):
            if re.fullmatch(r"E\d+", e) and e not in events:
                problems.append(f"catalog Event {e} is missing from Events")

    seen: set[str] = set()
    for i in ids:
        if i and i in seen:
            problems.append(f"ID {i} used twice")
        seen.add(i)
    if depth == "full" and "Flow" in sections and not re.search(r"```mermaid\s*\n\s*flowchart\s+LR", sections["Flow"]):
        problems.append("Flow has no mermaid flowchart LR")
    return problems


def board_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    first = path.read_text(encoding="utf-8").splitlines()[:1]
    m = re.search(r"Status:\s*(round\s+\d+|checkpoint|revision\s+\d+|review|done)\s*(\||$)", first[0]) if first else None
    return m.group(1) if m else "unreadable"


def status(folder: Path) -> dict:
    rows, catalog_problems = read_catalog(folder)
    root_board = board_status(folder / "board.md")
    out = {"catalog": rows is not None, "catalog_draft": (folder / "design-level-catalog.draft.md").is_file(),
           "catalog_problems": catalog_problems, "catalog_stale": [],
           "big_picture_done": root_board == "done", "contexts": [], "next_target": None, "all_done": False}
    if rows is None:
        return out
    known = context_map_ids(folder) or {}
    for bc, name in known.items():
        if not any(r.get("BC") == bc for r in rows):
            out["catalog_stale"].append(f"{bc} {name} is in context-map.md but not in the catalog")
    for r in rows:
        if r.get("BC") in known and known[r["BC"]] != r.get("Context"):
            out["catalog_stale"].append(f"{r['BC']} is '{known[r['BC']]}' in context-map.md, '{r.get('Context')}' in the catalog")
    for r in rows:
        f = r.get("Folder", "")
        ctx = folder / f if f else None
        rounds = sorted(p.name for p in (ctx / "rounds").iterdir() if p.is_dir()) if ctx and (ctx / "rounds").is_dir() else []
        b = board_status(ctx / "board.md") if ctx else None
        ok = bool(f) and not check_context(folder, f, r)
        done = ok and b == "done"
        out["contexts"].append({"bc": r.get("BC"), "context": r.get("Context"), "folder": f, "depth": r.get("Depth"),
                                "order": r.get("Order"), "board_status": b,
                                "last_round_folder": rounds[-1] if rounds else None, "design_ok": ok, "done": done})
    full = sorted((c for c in out["contexts"] if c["depth"] == "full"),
                  key=lambda c: int(c["order"]) if (c["order"] or "").isdigit() else 999)
    lean = [c for c in out["contexts"] if c["depth"] == "lean"]
    pending = [c for c in full + lean if not c["done"]]
    out["next_target"] = pending[0]["folder"] if pending else None
    out["all_done"] = bool(out["contexts"]) and not pending and not catalog_problems and not out["catalog_stale"]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, type=Path, help="the domain model folder")
    parser.add_argument("--context", help="one context folder, e.g. bc01-ordering")
    parser.add_argument("--status", action="store_true", help="report run state and next target")
    args = parser.parse_args()
    if not args.folder.is_dir():
        print(json.dumps({"ok": False, "error": f"folder not found: {args.folder}"}))
        return 2
    try:
        if args.status:
            print(json.dumps(status(args.folder), indent=2, ensure_ascii=False))
            return 0
        rows, catalog_problems = read_catalog(args.folder)
        by_folder = {r["Folder"]: r for r in rows or [] if r.get("Folder")}
        if args.context:
            names = [clean_folder(args.context)]
            catalog_problems = []
        elif rows is not None:
            names = [r["Folder"] for r in rows if r.get("Folder")]
        else:
            names = sorted(p.name for p in args.folder.iterdir() if p.is_dir() and FOLDER.match(p.name))
        results = [{"context": n, "problems": check_context(args.folder, n, by_folder.get(n))} for n in names]
    except (OSError, UnicodeDecodeError) as exc:
        print(json.dumps({"ok": False, "error": f"unreadable: {exc}"}))
        return 2
    for r in results:
        r["ok"] = not r["problems"]
    out = {"ok": bool(results) and not catalog_problems and all(r["ok"] for r in results),
           "catalog_problems": catalog_problems, "contexts": results,
           "missing": [] if results else ["no context found"]}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
