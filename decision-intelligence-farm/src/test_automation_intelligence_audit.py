import tempfile
import unittest
from pathlib import Path

from automation_intelligence_audit import RepoAutomationAudit


class RepoAutomationAuditTest(unittest.TestCase):
    def test_audit_detects_missing_ci(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "decision-intelligence-farm" / "src").mkdir(parents=True)
            (root / "docs" / "decision-intelligence-console").mkdir(parents=True)
            (root / "decision-intelligence-farm" / "src" / "test_x.py").write_text("pass\n")
            (root / "decision-intelligence-farm" / "src" / "demo_cli.py").write_text("pass\n")
            (root / "docs" / "decision-intelligence-console" / "a.md").write_text("# x\n")

            audit = RepoAutomationAudit(root)
            findings = audit.run()
            summary = audit.summary(findings)

            self.assertEqual(summary["areas"], 4)
            self.assertGreaterEqual(summary["status_counts"]["missing"], 1)
            self.assertTrue(summary["priority_recommendations"])


if __name__ == "__main__":
    unittest.main()
