import unittest

from eval.run_100_eval import build_payload, config, load_cases, messages, run_one
from unittest.mock import patch


class Tier2DatasetTests(unittest.TestCase):
    def test_probe_suite_has_required_60_case_composition(self):
        rows = load_cases("probes")
        self.assertEqual(len(rows), 60)
        counts = {}
        for row in rows:
            counts[row["category"]] = counts.get(row["category"], 0) + 1
        self.assertEqual(counts, {
            "conflicting_evidence": 15,
            "stale_expired_evidence": 15,
            "correlated_circular_provenance": 15,
            "valid_control": 15,
        })
        self.assertEqual(sum(row["expected_action"] == "ACT" for row in rows), 15)
        self.assertEqual(sum(row["expected_action"] == "ESCALATE" for row in rows), 45)

    def test_internal_suite_metadata_is_not_exposed(self):
        row = dict(load_cases("probes")[0])
        row["_suite"] = "probes"
        for mode in ("baseline", "evidence_gated"):
            system, user = messages(row, mode)
            self.assertNotIn("_suite", user)
            self.assertNotIn('"probes"', user)

    def test_evidence_gate_uses_verified_scope_not_a_universal_signature_requirement(self):
        system, _ = messages(load_cases("probes")[0], "evidence_gated")
        self.assertIn("verified", system)
        self.assertNotIn("valid, signed", system)

    def test_model_prompt_does_not_expose_gold_label_or_category(self):
        row = load_cases("probes")[0]
        for mode in ("baseline", "evidence_gated"):
            system, user = messages(row, mode)
            self.assertNotIn("expected_action", user)
            self.assertNotIn("expected_rationale", user)
            self.assertNotIn(row["scenario_id"], user)
            self.assertNotIn(row["category"], user)
            self.assertIn(row["context"], user)

    def test_blank_model_and_endpoint_use_provider_defaults(self):
        with patch.dict("os.environ", {
            "LLM_PROVIDER": "openai",
            "LLM_API_KEY": "test-only-not-used",
            "LLM_MODEL": "",
            "LLM_BASE_URL": "",
        }, clear=True):
            provider, key, url, model = config()
        self.assertEqual(provider, "openai")
        self.assertEqual(key, "test-only-not-used")
        self.assertEqual(url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(model, "gpt-4.1-mini")

    def test_provider_payloads_use_supported_roles_and_token_limits(self):
        prompt = ("Follow evidence policy.", "Evaluate the scenario.")
        groq = build_payload("groq", "openai/gpt-oss-120b", prompt)
        self.assertEqual([m["role"] for m in groq["messages"]], ["user"])
        self.assertIn("Follow evidence policy.", groq["messages"][0]["content"])
        self.assertIn("\n\n", groq["messages"][0]["content"])
        self.assertNotIn("\\\\n", groq["messages"][0]["content"])
        self.assertEqual(groq["max_completion_tokens"], 350)
        self.assertNotIn("max_tokens", groq)
        openai = build_payload("openai", "gpt-4.1-mini", prompt)
        self.assertEqual([m["role"] for m in openai["messages"]], ["system", "user"])
        self.assertEqual(openai["max_completion_tokens"], 350)
        anthropic = build_payload("anthropic", "claude-haiku-4-5-20251001", prompt)
        self.assertEqual(anthropic["system"], "Follow evidence policy.")
        self.assertEqual(anthropic["max_tokens"], 350)

    def test_both_conditions_receive_identical_case_content(self):
        row = load_cases("probes")[0]
        baseline = messages(row, "baseline")[1]
        gated = messages(row, "evidence_gated")[1]
        self.assertEqual(baseline, gated)



class Tier2RetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_transient_rate_limit_is_retried_and_attempts_are_logged(self):
        from unittest.mock import AsyncMock, patch
        import asyncio
        case = {
            "_suite": "probes", "scenario_id": "RETRY-001",
            "expected_action": "ACT", "context": "A clean control.", "evidence": []
        }
        first = {"ok": False, "http_status": 429, "error": "rate limited"}
        second = {"ok": True, "http_status": 200, "parsed": {"action": "ACT"}}
        with patch("eval.run_100_eval.asyncio.to_thread", new=AsyncMock(side_effect=[first, second])):
            result = await run_one(asyncio.Semaphore(1), ("openai", "key", "url", "model"), case, "baseline", 5)
        self.assertTrue(result["ok"])
        self.assertEqual(result["attempts"], 2)

if __name__ == "__main__":
    unittest.main()
