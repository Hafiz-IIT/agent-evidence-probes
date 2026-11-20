import json
import unittest
from pathlib import Path

from eval.run_100_eval import decide, metrics

ROOT = Path(__file__).resolve().parents[1]


class EvaluationSuiteTests(unittest.TestCase):
    def test_probe_dataset_has_balanced_sixty_scenarios(self):
        payload = json.loads((ROOT / "data" / "probes_60.json").read_text(encoding="utf-8"))
        scenarios = payload["scenarios"]
        self.assertEqual(payload["count"], 60)
        self.assertEqual(len(scenarios), 60)
        self.assertEqual(len({s["id"] for s in scenarios}), 60)
        self.assertEqual({a: sum(s["expected_action"] == a for s in scenarios) for a in ("ACT", "VERIFY", "ESCALATE")},
                         {"ACT": 20, "VERIFY": 20, "ESCALATE": 20})

    def test_all_three_datasets_form_exactly_one_hundred_cases(self):
        from eval.run_100_eval import load_scenarios
        scenarios = load_scenarios(None)
        self.assertEqual(len(scenarios), 100)
        self.assertEqual(len({s["id"] for s in scenarios}), 100)
        self.assertEqual(
            {a: sum(s["expected_action"] == a for s in scenarios) for a in ("ACT", "VERIFY", "ESCALATE")},
            {"ACT": 33, "VERIFY": 34, "ESCALATE": 33},
        )

    def test_combined_deterministic_gate_matches_authored_labels(self):
        from eval.run_100_eval import load_scenarios
        scenarios = load_scenarios(None)
        rows = [{"expected_action": s["expected_action"], "predicted_action": decide(s, True)} for s in scenarios]
        result = metrics(rows)
        self.assertEqual(result["scenario_count"], 100)
        self.assertEqual(result["unsafe_action_rate"], 0.0)
        self.assertEqual(result["false_block_rate"], 0.0)
        self.assertEqual(result["exact_action_accuracy"], 1.0)

    def test_deterministic_modes_and_metric_denominators(self):
        payload = json.loads((ROOT / "data" / "probes_60.json").read_text(encoding="utf-8"))
        rows = payload["scenarios"]
        predictions = [{"expected_action": s["expected_action"], "predicted_action": decide(s, True)} for s in rows]
        result = metrics(predictions)
        self.assertEqual(result["scenario_count"], 60)
        self.assertEqual(result["unsafe_action_denominator"], 40)
        self.assertEqual(result["false_block_denominator"], 20)
        self.assertGreaterEqual(result["unsafe_action_rate"], 0.0)
        self.assertLessEqual(result["unsafe_action_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
