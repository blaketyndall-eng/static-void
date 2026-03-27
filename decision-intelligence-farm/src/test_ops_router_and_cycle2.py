import tempfile
import unittest
from datetime import date
from pathlib import Path

from cadence_scheduler import CadenceScheduler
from dashboard_artifacts import build_dashboard
from drift_monitor import detect_ai_eval_drift, detect_delivery_drift
from automation_intelligence_audit import RepoAutomationAudit


class Cycle2ModulesTest(unittest.TestCase):
    def test_dashboard_alerts(self):
        dash = build_dashboard(
            execution_summary={"delivery_rate": 0.9},
            quality_summary={"passed": True},
            supply_summary={"passed": True},
            ai_eval_summary={"pass_rate": 0.7},
            automation_audit_summary={"status_counts": {"missing": 1}},
        )
        self.assertTrue(dash["alerts"]["ai_eval_regression"])
        self.assertTrue(dash["alerts"]["automation_gap"])

    def test_cadence_scheduler(self):
        tasks = CadenceScheduler.build_schedule(date(2026, 3, 27))
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].name, "weekly_execution_review")

    def test_drift_detection(self):
        ai = detect_ai_eval_drift({"pass_rate": 0.9}, {"pass_rate": 0.8}, threshold=0.05)
        self.assertTrue(ai["regression"])
        delivery = detect_delivery_drift({"delivery_rate": 0.8}, {"delivery_rate": 0.85})
        self.assertFalse(delivery["regression"])

    def test_audit_ci_present(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "decision-intelligence-farm" / "src").mkdir(parents=True)
            (root / "docs" / "decision-intelligence-console").mkdir(parents=True)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "decision-intelligence-farm" / "src" / "test_x.py").write_text("pass\n")
            (root / "decision-intelligence-farm" / "src" / "demo_cli.py").write_text("pass\n")
            (root / "docs" / "decision-intelligence-console" / "a.md").write_text("# x\n")
            (root / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")

            findings = RepoAutomationAudit(root).run()
            ci = [f for f in findings if f.area == "ci_automation"][0]
            self.assertEqual(ci.status, "present")


if __name__ == "__main__":
    unittest.main()
