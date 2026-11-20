import unittest

from benchmark import evaluate_scenarios, synthetic_scenarios


class BenchmarkTests(unittest.TestCase):
    def test_reference_scenarios_match_expected_decisions(self):
        now = 1000.0
        result = evaluate_scenarios(synthetic_scenarios(now=now), now=now)
        self.assertEqual(result["total"], 6)
        self.assertEqual(result["correct"], 5)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["unsafe_action_rate"], 0.0)
        self.assertEqual(result["false_block_rate"], 0.0)
        self.assertEqual(result["unsafe_action_denominator"], 5)
        self.assertEqual(result["valid_control_denominator"], 1)


if __name__ == "__main__":
    unittest.main()
