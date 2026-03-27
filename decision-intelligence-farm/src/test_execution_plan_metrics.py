import unittest

from execution_plan import ExecutionPlanManager


class ExecutionPlanMetricsTest(unittest.TestCase):
    def test_compute_reliability_metrics_empty(self):
        metrics = ExecutionPlanManager.compute_reliability_metrics([])
        self.assertEqual(metrics["deployment_frequency_per_week"], 0.0)
        self.assertEqual(metrics["change_failure_rate"], 0.0)
        self.assertEqual(metrics["mean_lead_time_hours"], 0.0)
        self.assertEqual(metrics["restoration_rate"], 0.0)

    def test_compute_reliability_metrics_populated(self):
        cards = [
            {
                "deployments": 5,
                "failed_deployments": 1,
                "restored_incidents": 1,
                "total_lead_time_hours": 40,
            },
            {
                "deployments": 3,
                "failed_deployments": 1,
                "restored_incidents": 1,
                "total_lead_time_hours": 24,
            },
        ]
        metrics = ExecutionPlanManager.compute_reliability_metrics(cards)
        self.assertEqual(metrics["deployment_frequency_per_week"], 4.0)
        self.assertEqual(metrics["change_failure_rate"], 0.25)
        self.assertEqual(metrics["mean_lead_time_hours"], 8.0)
        self.assertEqual(metrics["restoration_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
