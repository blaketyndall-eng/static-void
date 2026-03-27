import unittest

from quality_gates import ChangeEnvelope, QualityGatePolicy, RiskTier


class QualityGatePolicyTest(unittest.TestCase):
    def test_core_requires_full_checklist(self):
        env = ChangeEnvelope(
            risk_tier=RiskTier.CORE,
            tests_passed=True,
            lint_passed=True,
            build_passed=True,
            observability_verified=False,
            rollback_validated=False,
            critical_regression_tests_passed=False,
            security_scan_passed=True,
        )
        result = QualityGatePolicy.evaluate(env)
        self.assertFalse(result.passed)
        self.assertIn("observability_verified", result.failed_checks)
        self.assertIn("rollback_validated", result.failed_checks)
        self.assertIn("critical_regression_tests_passed", result.failed_checks)

    def test_low_tier_baseline(self):
        env = ChangeEnvelope(
            risk_tier=RiskTier.LOW,
            tests_passed=True,
            lint_passed=True,
            build_passed=True,
        )
        result = QualityGatePolicy.evaluate(env)
        self.assertTrue(result.passed)
        self.assertEqual(result.failed_checks, [])


if __name__ == "__main__":
    unittest.main()
