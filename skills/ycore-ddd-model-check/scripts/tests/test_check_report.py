import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_report.py"

HEADER = ("| ID | Check | Severity | Context | Code location | Model counterpart | Boundary "
          "| Finding | Direction or question |\n|---|---|---|---|---|---|---|---|---|\n")


def report(rows: str, sound: str = "Check 1: names match.\nCheck 3: all enforced.",
           not_checked: str = "Check 5: no plan.") -> str:
    return (f"# Review\n\n## Frame\nmode epic 1\n\n## Findings\n{HEADER}{rows}\n"
            f"## Checked and sound\n{sound}\n\n## Not assignable\nnone\n\n"
            f"## Not checked\n{not_checked}\n\n## Tally\n")


class CheckReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "order.py").write_text("\n".join(f"line {i}" for i in range(20)))

    def tearDown(self):
        self.tmp.cleanup()

    def run_on(self, text: str):
        path = self.root / "review.md"
        path.write_text(text)
        proc = subprocess.run([sys.executable, str(SCRIPT), "--report", str(path),
                               "--project-root", str(self.root)], capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def test_clean_report_tallies(self):
        rows = ("| FM-1 | 2 | high | Ordering | src/order.py:3-5 | context-map.md K-1 | yes | x | y |\n"
                "| FM-2 | 4 | low | Ordering | src/order.py:7 | context-map.md K-2 | yes | x | y |\n")
        code, out = self.run_on(report(rows))
        self.assertEqual(code, 0, out)
        self.assertEqual(out["tally"]["total"], 2)
        self.assertEqual(out["tally"]["boundary"], 2)
        self.assertEqual(out["tally"]["by_severity"]["high"], 1)

    def test_missing_location_and_bad_boundary(self):
        rows = ("| FM-1 | 2 | high | Ordering | src/order.py:3 | K-1 | no | x | y |\n"
                "| FM-2 | 3 | medium | Ordering | src/missing.py:1 | design.md A-1 | no | x | y |\n"
                "| FM-3 | 3 | low | Ordering | src/order.py:50 | design.md A-1 | no | x | y |\n")
        code, out = self.run_on(report(rows))
        self.assertEqual(code, 1)
        problems = {f["id"]: " ".join(f["problems"]) for f in out["findings"]}
        self.assertIn("does not fit check 2", problems["FM-1"])
        self.assertIn("not found", problems["FM-2"])
        self.assertIn("outside file", problems["FM-3"])

    def test_check_five_without_code_location(self):
        rows = "| FM-1 | 5 | medium | Billing | - | Billing/design.md Invoice | no | x | y |\n"
        code, out = self.run_on(report(rows, sound="Check 1: ok.\nCheck 2: ok.\nCheck 3: ok.\nCheck 4: ok.", not_checked="none"))
        self.assertEqual(code, 0, out)

    def test_unaccounted_checks_and_missing_section(self):
        text = report("", sound="Check 1: ok.", not_checked="none").replace("## Not assignable", "## Other")
        code, out = self.run_on(text)
        self.assertEqual(code, 1)
        self.assertEqual(out["sections_missing"], ["Not assignable"])
        self.assertEqual(out["checks_unaccounted"], [2, 3, 4, 5])

    def test_escaped_pipe_stays_in_cell_and_extra_cell_flagged(self):
        rows = ("| FM-1 | 2 | low | Ordering | src/order.py:3 | K-1 | yes | `a \\| b` | y |\n"
                "| FM-2 | 2 | low | Ordering | src/order.py:3 | K-1 | yes | a | b | y |\n")
        code, out = self.run_on(report(rows))
        self.assertEqual(code, 1)
        self.assertEqual([f["id"] for f in out["findings"]], ["FM-2"])

    def test_check_mentioned_mid_sentence_does_not_count(self):
        text = report("", sound="Check 1: ok.\nCheck 2: ok.\nCheck 3: ok, as in check 4.",
                      not_checked="Check 5: no plan.")
        code, out = self.run_on(text)
        self.assertEqual(out["checks_unaccounted"], [4])

    def test_missing_report(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--report", str(self.root / "no.md"),
                               "--project-root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
