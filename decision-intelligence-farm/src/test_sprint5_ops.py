import unittest

from sprint5_ops import CapabilityScore, JourneyUXMetric, Sprint5Ops


class Sprint5OpsTest(unittest.TestCase):
    def test_capability_health(self):
        scores = [
            CapabilityScore("coding", "L2", evidence_count=3, delivery_score=0.8, quality_score=0.9),
            CapabilityScore("debugging", "L2", evidence_count=2, delivery_score=0.7, quality_score=0.8),
        ]
        report = Sprint5Ops.capability_health(scores)
        self.assertEqual(report["tracks"], 2)
        self.assertIn("coding", report["advancement_ready_tracks"])

    def test_ux_improvement_report(self):
        metrics = [
            JourneyUXMetric("journey_a", 0.5, 0.8, 15, 10),
            JourneyUXMetric("journey_b", 0.7, 0.75, 12, 11),
        ]
        report = Sprint5Ops.ux_improvement_report(metrics)
        self.assertEqual(report["journeys"], 2)
        self.assertGreater(report["success_lift"], 0)
        self.assertGreater(report["time_reduction"], 0)


if __name__ == "__main__":
    unittest.main()
