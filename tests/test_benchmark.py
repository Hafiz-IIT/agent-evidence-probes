import unittest

from benchmark import evaluate_scenarios, synthetic_scenarios


class BenchmarkTests(unittest.TestCase):
    def test_reference_scenarios_match_expected_decisions(self):
        now = 1000.0
        result = evaluate_scenarios(synthetic_scenarios(now=now), now=now)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["correct"], 2)
        self.assertEqual(result["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
