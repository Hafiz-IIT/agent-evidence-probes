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
            Evidence("valid", "registry", 0.99, self.now, independent_group="registry", claim_key="document_validity"),
            Evidence("invalid", "inspection", 0.95, self.now, independent_group="inspection", claim_key="document_validity"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.decision, Decision.ESCALATE)

    def test_expired_evidence_is_ignored(self):
        evidence = [
            Evidence("valid", "old", 0.99, self.now - 100, ttl_seconds=10),
            Evidence("valid", "new", 0.99, self.now, independent_group="new"),
        ]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.fresh_count, 1)
        self.assertEqual(result.decision, Decision.VERIFY)

    def test_future_dated_evidence_is_not_fresh(self):
        evidence = [Evidence("valid", "future", 0.99, self.now + 10)]
        result = probe(evidence, "valid", now=self.now)
        self.assertEqual(result.fresh_count, 0)
        self.assertEqual(result.decision, Decision.VERIFY)

    def test_distinct_propositions_are_not_automatically_conflicts(self):
        evidence = [
            Evidence("shipment weight is 1000 kg", "invoice", 0.9, self.now),
            Evidence("consignee is ACME", "packing-list", 0.9, self.now),
        ]
        result = probe(evidence, "shipment weight is 1000 kg", now=self.now)
        self.assertEqual(result.decision, Decision.VERIFY)
        self.assertEqual(result.conflicting_claims, ())

    def test_invalid_confidence_and_ttl_are_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("valid", "source", 1.2, self.now)
        with self.assertRaises(ValueError):
            Evidence("valid", "source", 0.9, self.now, ttl_seconds=-1)

    def test_threshold_and_source_count_are_validated(self):
        with self.assertRaises(ValueError):
            probe([], "valid", act_threshold=1.1, now=self.now)
        with self.assertRaises(ValueError):
            probe([], "valid", min_independent_sources=0, now=self.now)


if __name__ == "__main__":
    unittest.main()
