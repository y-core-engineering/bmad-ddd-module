import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scope.py"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


class ScopeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        self.write("src/ordering/order.py", "x = 1\n")
        self.write("README.md", "readme\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.write("src/ordering/order.py", "x = 2\n")
        self.write("src/billing/invoice.py", "y = 1\n")
        self.write("tools/build.sh", "echo\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "epic work")
        self.plans = Path(self.tmp.name) / "epic-1"
        self.plans.mkdir()
        self.map = Path(self.tmp.name) / "code-map.md"
        self.map.write_text("# Code map\n\n| Context | Path |\n| --- | --- |\n"
                            "| BC01 Ordering | src/ordering |\n| BC02 Billing | src/billing/*.py |\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def plan(self, name, baseline, ticket="1.1"):
        (self.plans / name).write_text(f"---\ntitle: 't'\nticket: '{ticket}'\nstatus: 'built'\n"
                                       f"baseline_revision: '{baseline}' # the commit\n---\n\nbody\n")

    def run_scope(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args, "--repo", str(self.repo)],
                              capture_output=True, text=True)
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout else None), proc.stderr

    def test_epic_range_and_mapping(self):
        self.plan("plan-a.md", self.base)
        self.plan("plan-b.md", git(self.repo, "rev-parse", "HEAD"), ticket="1.2")
        code, out, _ = self.run_scope("epic", "--plans", str(self.plans), "--map", str(self.map))
        self.assertEqual(code, 0)
        self.assertEqual(out["range"]["from"], self.base)
        self.assertTrue(out["range"]["to_derived"])
        self.assertEqual(out["contexts"], {"BC01 Ordering": ["src/ordering/order.py"],
                                           "BC02 Billing": ["src/billing/invoice.py"]})
        self.assertEqual(out["unassigned"], ["tools/build.sh"])
        statuses = {f["path"]: f["status"] for f in out["files"]}
        self.assertEqual(statuses["src/billing/invoice.py"], "A")

    def test_plan_without_baseline_is_noted(self):
        self.plan("plan-a.md", self.base)
        self.plan("plan-b.md", "")
        code, out, _ = self.run_scope("epic", "--plans", str(self.plans))
        self.assertEqual(code, 0)
        self.assertFalse(out["mapped"])
        self.assertTrue(any("no baseline_revision" in n for n in out["notes"]))
        self.assertEqual(len(out["unassigned"]), 3)

    def test_no_plan_is_an_error(self):
        code, out, err = self.run_scope("epic", "--plans", str(self.plans))
        self.assertEqual(code, 2)
        self.assertIn("no build plan", err)

    def test_codebase_and_range(self):
        code, out, _ = self.run_scope("codebase", "--map", str(self.map))
        self.assertIn("README.md", out["unassigned"])
        code, out, _ = self.run_scope("range", "--range", f"{self.base}..HEAD")
        self.assertEqual(len(out["files"]), 3)
        self.assertFalse(out["range"]["to_derived"])

    def test_longest_entry_wins_and_map_without_table(self):
        self.map.write_text("| Context | Path |\n| --- | --- |\n| BC01 | src |\n| BC02 | src/billing |\n")
        code, out, _ = self.run_scope("codebase", "--map", str(self.map))
        self.assertIn("src/billing/invoice.py", out["contexts"]["BC02"])
        self.map.write_text("no table here\n")
        code, out, _ = self.run_scope("codebase", "--map", str(self.map))
        self.assertFalse(out["mapped"])
        self.assertTrue(out["notes"])


if __name__ == "__main__":
    unittest.main()
