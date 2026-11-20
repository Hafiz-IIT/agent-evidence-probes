import time
import unittest

from agent_evidence_probes import Decision, Evidence, probe


class EvidenceProbeTests(unittest.TestCase):
    def setUp(self):
        self.now = 1_000_000.0

    def test_independent_high_confidence_support_can_act(self):
        evidence = [
            Evidence("valid", "extractor", 0.95, self.now, independent_group="model"),
            Evidence("valid", "registry", 0.90, self.now, independent_group="external"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.decision, Decision.ACT)
        self.assertEqual(result.independent_count, 2)
        self.assertGreaterEqual(result.support_score, 0.90)

    def test_duplicate_source_does_not_count_as_independent(self):
        evidence = [
            Evidence("valid", "a", 0.99, self.now, independent_group="same"),
            Evidence("valid", "b", 0.99, self.now, independent_group="same"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.decision, Decision.VERIFY)
        self.assertEqual(result.independent_count, 1)

    def test_conflict_escalates(self):
        evidence = [
            Evidence("valid", "registry", 0.99, self.now, independent_group="registry", claim_key="shipment_status"),
            Evidence("invalid", "inspection", 0.95, self.now, independent_group="inspection", claim_key="shipment_status"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.decision, Decision.ESCALATE)

    def test_different_claim_keys_are_not_false_conflicts(self):
        evidence = [
            Evidence("valid", "registry", 0.99, self.now, independent_group="registry", claim_key="shipment_status"),
            Evidence("valid", "inspection", 0.95, self.now, independent_group="inspection", claim_key="shipment_status"),
            Evidence("1200kg", "scale", 0.99, self.now, independent_group="scale", claim_key="gross_weight"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.conflicting_claims, ())
        self.assertEqual(result.decision, Decision.ACT)

    def test_empty_claim_key_is_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("valid", "registry", 0.9, self.now, claim_key=" ")

    def test_future_dated_evidence_is_not_fresh(self):
        evidence = [
            Evidence("valid", "future-a", 0.99, self.now + 100, independent_group="a"),
            Evidence("valid", "future-b", 0.99, self.now + 100, independent_group="b"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.fresh_count, 0)
        self.assertEqual(result.decision, Decision.VERIFY)

    def test_invalid_evidence_values_rejected(self):
        for args in [
            ("valid", "a", float("nan"), self.now),
            ("valid", "a", 1.1, self.now),
            ("valid", "a", 0.9, self.now, -1),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Evidence(*args)

    def test_invalid_probe_thresholds_rejected(self):
        with self.assertRaises(ValueError):
            probe([], "valid", act_threshold=float("nan"), now=self.now)
        with self.assertRaises(ValueError):
            probe([], "valid", min_independent_sources=True, now=self.now)

    def test_expired_evidence_is_ignored(self):
        evidence = [
            Evidence("valid", "old", 0.99, self.now - 100, ttl_seconds=10),
            Evidence("valid", "new", 0.99, self.now, independent_group="new"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.fresh_count, 1)
        self.assertEqual(result.decision, Decision.VERIFY)


if __name__ == "__main__":
    unittest.main()
