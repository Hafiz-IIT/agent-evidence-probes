"""Unit tests for the Tier 2 runner's parsing, prompt isolation and metrics."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tier2_runner", ROOT / "eval" / "run_100_eval.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class Tier2RunnerTests(unittest.TestCase):
    def test_parse_valid_json_and_fenced_json(self):
        self.assertEqual(RUNNER.parse_response('{"action":"ACT","reason":"ok"}')["action"], "ACT")
        fenced = chr(96) * 3 + "json\n{\"action\":\"ESCALATE\"}\n" + chr(96) * 3
        self.assertEqual(RUNNER.parse_response(fenced)["action"], "ESCALATE")

    def test_parse_rejects_unknown_action(self):
        self.assertEqual(RUNNER.parse_response('{"action":"VERIFY"}')["action"], "INVALID")

    def test_prompt_hides_gold_labels_and_category(self):
        case = {
            "scenario_id": "SECRET-ID",
            "category": "SECRET-CATEGORY",
            "risk_flags": ["SECRET-RISK"],
            "expected_action": "ESCALATE",
            "expected_rationale": "SECRET-REASON",
            "context": "A document conflict exists.",
            "evidence": [],
            "decision_question": "May the agent proceed?",
        }
        _, prompt = RUNNER.messages(case, "evidence_gated")
        for secret in ("SECRET-ID", "SECRET-CATEGORY", "SECRET-RISK", "SECRET-REASON"):
            self.assertNotIn(secret, prompt)
        payload = json.loads(prompt)
        for hidden_key in ("scenario_id", "category", "risk_flags", "expected_action", "expected_rationale"):
            self.assertNotIn(hidden_key, payload)
        self.assertIn("A document conflict exists.", prompt)

    def test_metrics_keep_invalid_outputs_out_of_conditional_denominators(self):
        rows = [
            {"ok": True, "parsed": {"action": "ACT"}, "expected_action": "ESCALATE"},
            {"ok": False, "parsed": {"action": "INVALID"}, "expected_action": "ESCALATE"},
            {"ok": True, "parsed": {"action": "ESCALATE"}, "expected_action": "ACT"},
            {"ok": True, "parsed": {"action": "ACT"}, "expected_action": "ACT"},
        ]
        result = RUNNER.metrics(rows)
        self.assertEqual(result["unsafe_actions"], 1)
        self.assertEqual(result["unsafe_action_denominator"], 1)
        self.assertEqual(result["unscored_escalation_cases"], 1)
        self.assertEqual(result["false_blocks"], 1)
        self.assertEqual(result["valid_control_denominator"], 2)
        self.assertEqual(result["api_or_parse_failures"], 1)

    def test_retry_policy_is_narrow(self):
        self.assertTrue(RUNNER.is_retryable_error("groq", {"http_status": 429, "error": "rate limit"}))
        self.assertTrue(RUNNER.is_retryable_error("groq", {
            "http_status": 400,
            "error": json.dumps({"error": {"code": "json_validate_failed", "failed_generation": ""}}),
        }))
        self.assertFalse(RUNNER.is_retryable_error("groq", {
            "http_status": 400,
            "error": json.dumps({"error": {"code": "json_validate_failed", "failed_generation": "bad output"}}),
        }))
        self.assertFalse(RUNNER.is_retryable_error("groq", {"http_status": 401, "error": "unauthorized"}))

    def test_loader_rejects_non_object_evidence_items(self):
        categories = (
            ["conflicting_evidence"] * 15
            + ["stale_expired_evidence"] * 15
            + ["correlated_circular_provenance"] * 15
            + ["valid_control"] * 15
        )
        cases = []
        for index, category in enumerate(categories):
            cases.append({
                "scenario_id": f"TEST-{index:03d}",
                "category": category,
                "expected_action": "ACT" if category == "valid_control" else "ESCALATE",
                "context": "Synthetic test context.",
                "evidence": ["not-an-object"] if index == 0 else [],
            })
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps({"scenarios": cases}), encoding="utf-8")
            previous = RUNNER.SUITES["probes"]
            RUNNER.SUITES["probes"] = [path]
            try:
                with self.assertRaisesRegex(ValueError, "evidence item must be an object"):
                    RUNNER.load_cases("probes")
            finally:
                RUNNER.SUITES["probes"] = previous


if __name__ == "__main__":
    unittest.main()
