import unittest

from ai_eval import AIEvalHarness, EvalCase


class AIEvalHarnessTest(unittest.TestCase):
    def test_pass_non_refusal_case(self):
        case = EvalCase(case_id="1", expected_keywords=["alpha", "beta"])
        result = AIEvalHarness.evaluate_case(case, "alpha beta gamma")
        self.assertTrue(result.passed)
        self.assertEqual(result.keyword_hit_rate, 1.0)

    def test_refusal_required_case(self):
        case = EvalCase(case_id="2", expected_keywords=["ignored"], must_refuse=True)
        result = AIEvalHarness.evaluate_case(case, "I cannot help with that")
        self.assertTrue(result.refused)
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
