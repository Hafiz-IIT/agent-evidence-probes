import unittest

from eval.run_100_eval import load_cases, messages


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

    def test_model_prompt_does_not_expose_gold_label_or_category(self):
        row = load_cases("probes")[0]
        for mode in ("baseline", "evidence_gated"):
            system, user = messages(row, mode)
            self.assertNotIn("expected_action", user)
            self.assertNotIn("expected_rationale", user)
            self.assertNotIn(row["scenario_id"], user)
            self.assertNotIn(row["category"], user)
            self.assertIn(row["context"], user)

    def test_both_conditions_receive_identical_case_content(self):
        row = load_cases("probes")[0]
        baseline = messages(row, "baseline")[1]
        gated = messages(row, "evidence_gated")[1]
        self.assertEqual(baseline, gated)


if __name__ == "__main__":
    unittest.main()
