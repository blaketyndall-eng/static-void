import tempfile
import unittest
from pathlib import Path

from checkpoint_integration import (
    build_experiment_backlog,
    persist_customer_snapshot,
    persist_gtm_backlog,
    promotion_decision_with_model_ops,
)
from customer_intelligence import FeedbackItem


class CheckpointIntegrationTest(unittest.TestCase):
    def test_backlog_generation(self):
        feedback = [
            FeedbackItem(source="call", text="pricing is too expensive", segment="smb"),
            FeedbackItem(source="ticket", text="pricing still confusing", segment="smb"),
        ]
        backlog = build_experiment_backlog(feedback)
        self.assertGreaterEqual(len(backlog), 1)
        self.assertTrue(backlog[0].name.startswith("pricing-test"))

    def test_persistence(self):
        feedback = [FeedbackItem(source="call", text="interface is confusing", segment="enterprise")]
        with tempfile.TemporaryDirectory() as td:
            c = persist_customer_snapshot(td, feedback)
            g = persist_gtm_backlog(td, build_experiment_backlog(feedback))
            self.assertTrue(Path(c).exists())
            self.assertTrue(Path(g).exists())

    def test_model_ops_hard_gate(self):
        out = promotion_decision_with_model_ops(
            quality_passed=True,
            supply_chain_passed=True,
            baseline_pass_rate=0.95,
            candidate_pass_rate=0.85,
            safety_incidents=0,
            delivery_rate=0.9,
        )
        self.assertFalse(out["promote"])
        self.assertIn("evaluation regression beyond threshold", out["blocked_reasons"])


if __name__ == "__main__":
    unittest.main()
