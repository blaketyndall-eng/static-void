import tempfile
import unittest
from pathlib import Path

from artifact_registry import ArtifactRegistry
from batch_executor import BatchJob, plan_batches
from governance_bot import recommend_actions
from pipeline_runner import PipelineRun
from promotion_engine import should_promote_release


class Cycle3SprintTest(unittest.TestCase):
    def test_pipeline_summary(self):
        run = PipelineRun(run_id="r1")
        run.mark("compile", "passed")
        run.mark("tests", "failed", "1 failing test")
        summary = run.summary()
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)

    def test_artifact_registry(self):
        with tempfile.TemporaryDirectory() as td:
            reg = ArtifactRegistry(Path(td))
            path = reg.register("dashboard", {"ok": True})
            self.assertTrue(path.exists())
            self.assertEqual(reg.latest("dashboard"), path)

    def test_governance_actions(self):
        actions = recommend_actions({"alerts": {"ai_eval_regression": True}})
        self.assertEqual(len(actions), 1)
        self.assertIn("freeze model promotion", actions[0])

    def test_batch_planning(self):
        jobs = [BatchJob("a", 5, 30), BatchJob("b", 3, 20), BatchJob("c", 4, 40)]
        batches = plan_batches(jobs, max_minutes_per_batch=60)
        self.assertGreaterEqual(len(batches), 2)

    def test_promotion_engine(self):
        out = should_promote_release(
            quality_passed=True,
            supply_chain_passed=True,
            ai_eval_pass_rate=0.9,
            delivery_rate=0.8,
        )
        self.assertTrue(out["promote"])


if __name__ == "__main__":
    unittest.main()
