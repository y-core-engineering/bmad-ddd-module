import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_artifacts.py"

CONTEXT_MAP = """# Context Map

## Contexts
| ID | Context | Subdomain | Responsibility | Most sensitive data | Protection need |
|---|---|---|---|---|---|
| BC01 | Ordering | Core | takes orders | address | high |
| BC02 | Billing | Supporting | invoices | IBAN | very high |
| X01 | Payment provider | External | card payments | card data | very high |

## Edges
| ID | From | To | Pattern | What flows | Trust boundary |
|---|---|---|---|---|---|
| K-01 | BC01 | BC02 | Customer/Supplier | OrderPlaced | no |
| K-02 | X01 | BC02 | Open Host Service / Anti-Corruption Layer | payment status | yes: other operator |

## Diagram
```mermaid
graph LR
  A --> B
```
"""

GLOSSARY = """# Ubiquitous Language

## BC01 Ordering
| Term | Definition | Conflicts |
|---|---|---|
| Order | a placed basket | BC02: invoice basis |

## BC02 Billing
| Term | Definition | Conflicts |
|---|---|---|
| Invoice | claim to pay | none |
"""

EVENTS = """# Event Storming

```mermaid
flowchart LR
  C1 --> E1
```

## BC01 Ordering
Events: E01

## BC02 Billing
Events: E05
"""


class CheckArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, cmap=CONTEXT_MAP, glossary=GLOSSARY, events=EVENTS):
        for name, text in (("context-map.md", cmap), ("ubiquitous-language.md", glossary),
                           ("event-storming.md", events)):
            if text is not None:
                (self.dir / name).write_text(text)

    def run_it(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--folder", str(self.dir)],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def test_clean_set(self):
        self.write()
        code, out = self.run_it()
        self.assertEqual(code, 0, out)

    def test_bad_cells(self):
        cmap = (CONTEXT_MAP.replace("| K-01 | BC01 | BC02 | Customer/Supplier | OrderPlaced | no |",
                                    "| K-01 | BC01 | BC09 | Friendship | OrderPlaced | maybe |")
                .replace("| BC02 | Billing | Supporting |", "| BC02 | Billing | Important |"))
        self.write(cmap=cmap)
        code, out = self.run_it()
        self.assertEqual(code, 1)
        rules = {(c["column"], c["value"]) for c in out["bad_cells"]}
        self.assertIn(("To", "BC09"), rules)
        self.assertIn(("Pattern", "Friendship"), rules)
        self.assertIn(("Trust boundary", "maybe"), rules)
        self.assertIn(("Subdomain", "Important"), rules)

    def test_missing_file_section_and_name_mismatch(self):
        self.write(events=None, glossary=GLOSSARY.replace("## BC02 Billing", "## BC02 Invoicing"))
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertEqual(out["files_missing"], ["event-storming.md"])
        self.assertTrue(any("Invoicing" in c["problem"] for c in out["cross_refs"]))

    def test_missing_column(self):
        self.write(cmap=CONTEXT_MAP.replace("| Protection need |\n", "|\n", 1))
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn({"file": "context-map.md", "table": "Contexts", "column": "Protection need"},
                      out["columns_missing"])

    def test_empty_map_is_a_gap(self):
        empty = ("## Contexts\n| ID | Context | Subdomain | Responsibility | Most sensitive data | Protection need |\n"
                 "|---|---|---|---|---|---|\n\n## Edges\n| ID | From | To | Pattern | What flows | Trust boundary |\n"
                 "|---|---|---|---|---|---|\n\n## Diagram\n```mermaid\ngraph LR\n```\n")
        self.write(cmap=empty, glossary="# UL\n", events="# ES\n```mermaid\nflowchart LR\n```\n")
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertTrue(any("no BC row" in c["problem"] for c in out["cross_refs"]))

    def test_row_rules(self):
        cmap = (CONTEXT_MAP
                .replace("| X01 | Payment provider | External |", "| X01 |  | Generic |")
                .replace("| K-02 | X01 | BC02 |", "| K-01 | BC01 | BC01 |")
                .replace("| BC02 | Billing |", "| Q02 | Billing |"))
        self.write(cmap=cmap)
        code, out = self.run_it()
        self.assertEqual(code, 1)
        rules = {(c["column"], c["rule"]) for c in out["bad_cells"]}
        self.assertIn(("Subdomain", "External for an X row"), rules)
        self.assertIn(("Context", "empty"), rules)
        self.assertIn(("ID", "repeated"), rules)
        self.assertIn(("To", "differs from From"), rules)
        self.assertIn(("ID", "BC## or X##"), rules)

    def test_diagram_duplicates_and_fenced_headings(self):
        cmap = CONTEXT_MAP.replace("```mermaid\ngraph LR\n  A --> B\n```", "no diagram here")
        glossary = GLOSSARY + "\n## BC01 Ordering\n| Term | Definition | Conflicts |\n|---|---|---|\n"
        events = EVENTS.replace("C1 --> E1", "C1 --> E1\n## BC09 Ghost")
        self.write(cmap=cmap, glossary=glossary, events=events)
        code, out = self.run_it()
        problems = " ".join(c["problem"] for c in out["cross_refs"])
        self.assertIn("no mermaid block", problems)
        self.assertIn("more than once", problems)
        self.assertNotIn("BC09", problems)

    def test_section_without_context_row(self):
        self.write(glossary=GLOSSARY + "\n## BC07 Shipping\n| Term | Definition | Conflicts |\n|---|---|---|\n")
        code, out = self.run_it()
        self.assertTrue(any("BC07 has no row" in c["problem"] for c in out["cross_refs"]))

    def test_missing_folder(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--folder", str(self.dir / "none")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
