import tempfile
import unittest

from checkpoint2_orchestrator import WeeklyLoopOrchestrator
from customer_intelligence import FeedbackItem


class Checkpoint2OrchestratorTest(unittest.TestCase):
    def test_weekly_loop_run(self):
        feedback = [
            FeedbackItem(source="call", text="pricing is too expensive", segment="smb"),
            FeedbackItem(source="ticket", text="interface is confusing", segment="enterprise"),
        ]
        with tempfile.TemporaryDirectory() as td:
            out = WeeklyLoopOrchestrator(td).run(
                run_id="wk-1",
                feedback=feedback,
                quality_passed=True,
                supply_chain_passed=True,
                baseline_pass_rate=0.92,
                candidate_pass_rate=0.91,
                safety_incidents=0,
                delivery_rate=0.85,
            )
            self.assertTrue(out["pipeline"]["total_steps"] >= 6)
            self.assertTrue(out["promotion"]["promote"])
            self.assertTrue(out["dashboard_path"].endswith(".json"))
            self.assertTrue(out["actions_path"].endswith(".json"))


if __name__ == "__main__":
    unittest.main()
