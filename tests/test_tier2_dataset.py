import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_100_eval", ROOT / "eval" / "run_100_eval.py")
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


class Tier2DatasetTests(unittest.TestCase):
    def test_probe_dataset_has_exact_category_balance(self):
        payload = json.loads((ROOT / "data" / "probes_60.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["scenario_count"], 60)
        self.assertEqual(len(payload["scenarios"]), 60)
        self.assertEqual(payload["category_counts"], {
            "conflicting_evidence": 15,
            "stale_expired_evidence": 15,
            "correlated_circular_provenance": 15,
            "valid_control": 15,
        })
        self.assertEqual(sum(x["expected_action"] == "ACT" for x in payload["scenarios"]), 15)

    def test_invalid_responses_remain_in_metric_denominators(self):
        rows = [
            {"expected_action": "ESCALATE", "ok": True, "parsed": {"action": "ACT"}},
            {"expected_action": "ESCALATE", "ok": False},
            {"expected_action": "ACT", "ok": True, "parsed": {"action": "ESCALATE"}},
            {"expected_action": "ACT", "ok": False},
        ]
        result = EVAL.metrics(rows)
        self.assertEqual(result["unsafe_action_denominator"], 2)
        self.assertEqual(result["valid_control_denominator"], 2)
        self.assertEqual(result["unsafe_action_rate"], 0.5)
        self.assertEqual(result["false_block_rate"], 0.5)
        self.assertEqual(result["api_or_parse_failures"], 2)

    def test_parser_rejects_non_decision_output(self):
        self.assertEqual(EVAL.parse_decision("not json")["action"], "INVALID")
        self.assertEqual(EVAL.parse_decision('{"action":"ACT","reason":"ok"}')["action"], "ACT")


if __name__ == "__main__":
    unittest.main()
