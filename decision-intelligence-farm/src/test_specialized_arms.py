import unittest

from customer_intelligence import CustomerIntelligence, FeedbackItem
from data_reliability import check_completeness, check_freshness
from model_ops import evaluate_model_release
from partner_arm import PartnerProfile, rank_partners
from revenue_gtm import GTMExperiment, summarize_experiments


class SpecializedArmsTest(unittest.TestCase):
    def test_customer_intelligence(self):
        items = [
            FeedbackItem(source="call", text="pricing is too expensive", segment="smb"),
            FeedbackItem(source="ticket", text="interface is confusing", segment="enterprise"),
        ]
        summary = CustomerIntelligence.summarize(items)
        self.assertEqual(summary["total_feedback"], 2)
        self.assertIn("pricing", summary["themes"])

    def test_revenue_gtm(self):
        exps = [
            GTMExperiment("a", "email", 100, 250, 0.04),
            GTMExperiment("b", "ads", 100, 150, 0.02),
        ]
        s = summarize_experiments(exps)
        self.assertEqual(s["best"], "a")

    def test_data_reliability(self):
        out = check_completeness([{"a": 1, "b": 2}, {"a": 1, "b": ""}], ["a", "b"])
        self.assertEqual(out["complete_ratio"], 0.5)
        fresh = check_freshness(12, max_age_hours=24)
        self.assertTrue(fresh["fresh"])

    def test_model_ops(self):
        verdict = evaluate_model_release(
            baseline_pass_rate=0.92,
            candidate_pass_rate=0.91,
            safety_incidents=0,
            max_drop=0.03,
        )
        self.assertTrue(verdict["promote"])

    def test_partner_arm(self):
        partners = [
            PartnerProfile("P1", integration_effort=2, market_reach=5, reliability_score=0.9),
            PartnerProfile("P2", integration_effort=4, market_reach=3, reliability_score=0.8),
        ]
        ranked = rank_partners(partners)
        self.assertEqual(ranked[0][0], "P1")


if __name__ == "__main__":
    unittest.main()
