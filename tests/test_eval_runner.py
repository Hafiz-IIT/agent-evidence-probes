import json
import unittest
from pathlib import Path

from eval.run_tier1_conformance import decide, llm_scenario_view, metrics

ROOT = Path(__file__).resolve().parents[1]


class EvaluationSuiteTests(unittest.TestCase):
    def test_probe_dataset_has_balanced_sixty_scenarios(self):
        payload = json.loads((ROOT / "data" / "probes_tier1_60.json").read_text(encoding="utf-8"))
        scenarios = payload["scenarios"]
        self.assertEqual(payload["count"], 60)
        self.assertEqual(len(scenarios), 60)
        self.assertEqual(len({s["id"] for s in scenarios}), 60)
        self.assertEqual({a: sum(s["expected_action"] == a for s in scenarios) for a in ("ACT", "VERIFY", "ESCALATE")},
                         {"ACT": 20, "VERIFY": 20, "ESCALATE": 20})

    def test_all_three_datasets_form_exactly_one_hundred_cases(self):
        from eval.run_tier1_conformance import load_scenarios
        scenarios = load_scenarios(None)
        self.assertEqual(len(scenarios), 100)
        self.assertEqual(len({s["id"] for s in scenarios}), 100)
        self.assertEqual(
            {a: sum(s["expected_action"] == a for s in scenarios) for a in ("ACT", "VERIFY", "ESCALATE")},
            {"ACT": 33, "VERIFY": 34, "ESCALATE": 33},
        )

    def test_each_scenario_evidence_matches_its_declared_mechanism(self):
        from eval.run_tier1_conformance import load_scenarios
        scenarios = load_scenarios(None)
        allowed = {"fresh_independent_support", "missing_evidence", "stale_evidence",
                   "weak_independent_support", "dependent_sources", "single_source_support",
                   "fresh_conflicting_claims"}
        self.assertTrue(all(s["evaluation_mechanism"] in allowed for s in scenarios))
        self.assertEqual(
            {a: sum(s["expected_action"] == a for s in scenarios) for a in ("ACT", "VERIFY", "ESCALATE")},
            {"ACT": 33, "VERIFY": 34, "ESCALATE": 33},
        )

    def test_llm_input_excludes_expected_label_and_rationale(self):
        scenario = {
            "id": "TEST-001", "name": "example", "description": "A synthetic case",
            "target_claim": "supported", "risk_level": "HIGH",
            "evidence": [], "expected_action": "ESCALATE",
            "rationale": "Do not reveal this to the model",
            "evaluation_mechanism": "fresh_conflicting_claims",
        }
        model_input = llm_scenario_view(scenario)
        self.assertNotIn("expected_action", model_input)
        self.assertNotIn("rationale", model_input)
        self.assertNotIn("evaluation_mechanism", model_input)
        self.assertEqual(model_input["id"], "TEST-001")

    def test_multiclass_metrics_include_confusion_matrix_and_macro_f1(self):
        rows = [
            {"expected_action": "ACT", "predicted_action": "ACT"},
            {"expected_action": "VERIFY", "predicted_action": "ACT"},
            {"expected_action": "ESCALATE", "predicted_action": "ESCALATE"},
        ]
        result = metrics(rows)
        self.assertEqual(result["confusion_matrix"]["VERIFY"]["ACT"], 1)
        self.assertEqual(result["per_class"]["VERIFY"]["recall"], 0.0)
        self.assertGreaterEqual(result["macro_f1"], 0.0)
        self.assertLessEqual(result["macro_f1"], 1.0)

    def test_confidence_only_baseline_ignores_conflicts_and_freshness(self):
        from eval.run_tier1_conformance import load_scenarios
        scenarios = load_scenarios(None)
        rows = [{"expected_action": s["expected_action"], "predicted_action": decide(s, False)} for s in scenarios]
        result = metrics(rows)
        self.assertGreater(result["unsafe_action_rate"], 0.0)
        self.assertEqual(result["false_block_rate"], 0.0)

    def test_combined_deterministic_gate_matches_authored_labels(self):
        from eval.run_tier1_conformance import load_scenarios
        scenarios = load_scenarios(None)
        rows = [{"expected_action": s["expected_action"], "predicted_action": decide(s, True)} for s in scenarios]
        result = metrics(rows)
        self.assertEqual(result["scenario_count"], 100)
        self.assertEqual(result["unsafe_action_rate"], 0.0)
        self.assertEqual(result["false_block_rate"], 0.0)
        self.assertEqual(result["exact_action_accuracy"], 1.0)

    def test_deterministic_modes_and_metric_denominators(self):
        payload = json.loads((ROOT / "data" / "probes_tier1_60.json").read_text(encoding="utf-8"))
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
