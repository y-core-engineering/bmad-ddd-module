import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_design.py"

FULL = """# BC01 Ordering · Design
Depth: full

## Aggregates
### BC01-AGG01 Order
Root: Order
Entities: OrderLine
Value Objects: Money

| ID | Invariant | Security | Source |
|---|---|---|---|
| BC01-INV01 | an order has at least one line | no | board E03 |
| BC01-INV02 | only the owning tenant reads an order | yes | constraint GDPR |

## Commands
| ID | Command | Actor | May | Aggregate | Events |
|---|---|---|---|---|---|
| BC01-C01 | Place order | Customer | logged-in customer of the tenant | BC01-AGG01 | E03 |

## Events
| ID | Event | Aggregate |
|---|---|---|
| E03 | Order placed | BC01-AGG01 |

## Policies
| ID | Whenever | Then |
|---|---|---|
| BC01-P01 | E03 | BC02-C01 |

## Read Models
| ID | Read Model | Serves | Content |
|---|---|---|---|
| BC01-R01 | Cart | Customer | lines and prices |

## External Systems and ACLs
| ID | System | ACL translates | Kept out |
|---|---|---|---|
| X01 | Payment provider | payment status | card data |

## Abuse cases
| ID | Abuse case | STRIDE | Prevented by | Protection need |
|---|---|---|---|---|
| BC01-M01 | Foreign tenant sees order | I, E | BC01-INV02 | high |

## Hotspots
| ID | Question | Status | Decision |
|---|---|---|---|
| H04 | Partial delivery? | deferred | assume none; owner PO; returns at architecture |

## Flow
```mermaid
flowchart LR
  C1 --> AG1 --> E1
## BC09 not a section
```

## Implementation order
Order first.
"""

LEAN = """# BC03 Notification · Design
Depth: lean

## Why lean
Generic, bought in.

## Aggregates
### BC03-AGG01 Message
Root: Message
Entities: none
Value Objects: Address

## Commands
| ID | Command | Actor | May | Aggregate | Events |
|---|---|---|---|---|---|
| BC03-C01 | Send message | Policy | system only | BC03-AGG01 | E20 |

## External Systems and ACLs
| ID | System | ACL translates | Kept out |
|---|---|---|---|
| X02 | Mail service | delivery status | provider ids |

## Hotspots
| ID | Question | Status | Decision |
|---|---|---|---|
"""


class CheckDesignTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, folder, text):
        (self.dir / folder).mkdir(parents=True, exist_ok=True)
        (self.dir / folder / "design.md").write_text(text)

    def run_it(self, *extra):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--folder", str(self.dir), *extra],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def problems(self, out):
        return " | ".join(p for c in out["contexts"] for p in c["problems"])

    def test_full_and_lean_pass(self):
        self.put("bc01-ordering", FULL)
        self.put("bc03-notification", LEAN)
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        self.assertEqual(len(out["contexts"]), 2)

    def test_cell_rules(self):
        text = (FULL.replace("| no | board E03 |", "| maybe | board E03 |")
                .replace("| BC01-AGG01 | E03 |\n", "| BC01-AGG09 | E03 |\n")
                .replace("| I, E |", "| X |")
                .replace("| deferred |", "| later |")
                .replace("| logged-in customer of the tenant |", "|  |"))
        self.put("bc01-ordering", text)
        code, out = self.run_it("--context", "bc01-ordering")
        self.assertEqual(code, 1)
        p = self.problems(out)
        for expected in ("Security 'maybe'", "not defined here", "STRIDE 'X'", "status 'later'", "has no May"):
            self.assertIn(expected, p)

    def test_missing_sections_and_invariants_in_full(self):
        text = FULL.replace("## Abuse cases", "## Misuse").replace(
            "| BC01-INV01 | an order has at least one line | no | board E03 |\n"
            "| BC01-INV02 | only the owning tenant reads an order | yes | constraint GDPR |\n", "")
        self.put("bc01-ordering", text)
        code, out = self.run_it()
        p = self.problems(out)
        self.assertIn("section 'Abuse cases' missing", p)
        self.assertIn("BC01-AGG01 has no invariant", p)

    def test_wrong_prefix_title_and_duplicates(self):
        text = FULL.replace("# BC01 Ordering", "# BC02 Ordering").replace("BC01-C01", "BC02-C01").replace(
            "| BC01-R01 |", "| BC01-P01 |")
        self.put("bc01-ordering", text)
        code, out = self.run_it()
        p = self.problems(out)
        self.assertIn("first line", p)
        self.assertIn("Commands ID 'BC02-C01' does not match", p)
        self.assertIn("used twice", p)
        self.assertNotIn("BC09", p)

    def test_catalog_lists_missing_context(self):
        self.put("bc01-ordering", FULL)
        (self.dir / "design-level-catalog.md").write_text(
            "## Contexts\n| BC | Context | Folder |\n|---|---|---|\n"
            "| BC01 | Ordering | `bc01-ordering/` |\n| BC02 | Billing | bc02-billing |\n")
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("design.md missing", self.problems(out))

    def test_cross_references(self):
        text = (FULL.replace("| E03 | Order placed | BC01-AGG01 |",
                             "| E03 | Order placed | BC01-AGG01 |\n| E99 | Order lost | BC01-AGG77 |")
                .replace("| BC01-P01 | E03 | BC02-C01 |", "| BC01-P01 | whenever someone | x |")
                .replace("| I, E | BC01-INV02 |", "| I, I | nobody |")
                .replace("flowchart LR", "sequenceDiagram"))
        self.put("bc01-ordering", text)
        code, out = self.run_it()
        p = self.problems(out)
        for expected in ("E99 names aggregate 'BC01-AGG77'", "E99 is produced by no Command",
                         "reacts to 'whenever someone'", "Then 'x' is not a Command ID",
                         "not distinct letters", "names no invariant, Command or Hotspot",
                         "no mermaid flowchart LR"):
            self.assertIn(expected, p)

    def catalog(self, rows):
        header = ("## Contexts\n| BC | Context | Folder | Subdomain | MVP | Depth | Order | Events | "
                  "Aggregate candidates | Hotspots | External systems |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
        (self.dir / "design-level-catalog.md").write_text(header + "".join(rows))

    def test_lean_note_cannot_close_full_context(self):
        self.put("bc01-ordering", LEAN.replace("BC03", "BC01").replace("Notification", "Ordering"))
        self.catalog(["| BC01 | Ordering | `bc01-ordering/` | Core | yes | full | 1 | E03, E04 | Order | H04 | X01 |\n"])
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("differs from the catalog's 'full'", self.problems(out))

    def test_catalog_problems(self):
        self.catalog(["| BC01 | Ordering |  | Core | yes | full | first | E03 | - | - | - |\n",
                      "| BC02 | Bestellprüfung | bc02-bestellprüfung | Core | yes | lean | 2 | E05 | - | - | - |\n"])
        code, out = self.run_it()
        problems = " | ".join(out["catalog_problems"])
        self.assertIn("BC01 has no Folder", problems)
        self.assertIn("ascii-kebab-name", problems)
        self.assertIn("is lean but Order is '2'", problems)

    def test_status_routes_full_then_lean(self):
        self.put("bc01-ordering", FULL)
        self.put("bc03-notification", LEAN)
        (self.dir / "bc01-ordering" / "board.md").write_text("BC: BC01 Ordering | Status: checkpoint | open H04\n")
        (self.dir / "bc01-ordering" / "rounds" / "round-07").mkdir(parents=True)
        (self.dir / "context-map.md").write_text(
            "## Contexts\n| ID | Context |\n|---|---|\n| BC01 | Ordering |\n| BC03 | Notification |\n| BC04 | Billing |\n")
        self.catalog(["| BC01 | Ordering | bc01-ordering | Core | yes | full | 1 | E03 | - | - | - |\n",
                      "| BC03 | Notification | bc03-notification | Generic | no | lean | - | E20 | - | - | - |\n"])
        code, out = self.run_it("--status")
        self.assertEqual(code, 0)
        self.assertEqual(out["next_target"], "bc01-ordering")
        bc01 = out["contexts"][0]
        self.assertEqual((bc01["board_status"], bc01["last_round_folder"], bc01["done"]), ("checkpoint", "round-07", False))
        self.assertFalse(out["contexts"][1]["done"])
        self.assertTrue(any("BC04" in s for s in out["catalog_stale"]))
        (self.dir / "bc01-ordering" / "board.md").write_text("BC: BC01 Ordering | Status: done | ok\n")
        code, out = self.run_it("--status")
        self.assertEqual(out["next_target"], "bc03-notification")
        (self.dir / "bc03-notification" / "board.md").write_text("BC: BC03 Notification | Status: done | lean, confirmed\n")
        code, out = self.run_it("--status")
        self.assertIsNone(out["next_target"])
        self.assertFalse(out["all_done"])
        (self.dir / "context-map.md").write_text(
            "## Contexts\n| ID | Context |\n|---|---|\n| BC01 | Ordering |\n| BC03 | Notification |\n")
        code, out = self.run_it("--status")
        self.assertTrue(out["all_done"])

    def test_empty_catalog_draft_and_unreadable_board(self):
        self.catalog([])
        (self.dir / "design-level-catalog.draft.md").write_text("draft")
        code, out = self.run_it("--status")
        self.assertIn("catalog has no context rows", out["catalog_problems"])
        self.assertTrue(out["catalog_draft"])
        self.put("bc01-ordering", FULL)
        (self.dir / "bc01-ordering" / "board.md").write_text("# Board\nBC: BC01 | Status: reviewed\n")
        self.catalog(["| BC01 | Ordering | bc01-ordering | Core | yes | full | 1 | E03 | - | - | - |\n"])
        code, out = self.run_it("--status")
        self.assertEqual(out["contexts"][0]["board_status"], "unreadable")

    def test_context_with_trailing_slash(self):
        self.put("bc01-ordering", FULL)
        code, out = self.run_it("--context", "bc01-ordering/")
        self.assertEqual(code, 0, out)

    def test_bad_folder_and_empty(self):
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertEqual(out["missing"], ["no context found"])
        code, out = self.run_it("--context", "Ordering")
        self.assertIn("not bc##-<ascii-kebab-name>", self.problems(out))


if __name__ == "__main__":
    unittest.main()
