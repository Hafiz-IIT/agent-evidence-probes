import unittest

from agent_evidence_probes import Decision, Evidence, probe


class EvidenceProbePolicyTests(unittest.TestCase):
    NOW = 1000.0

    def item(self, claim="supported", source="s1", confidence=0.97, age=10, ttl=3600, group=None, claim_key=None):
        return Evidence(claim, source, confidence, self.NOW-age, ttl, group, claim_key)

    def test_two_fresh_independent_sources_allow_act(self):
        result = probe([self.item(source="a", group="a"), self.item(source="b", group="b")], "supported", now=self.NOW)
        self.assertEqual(result.decision, Decision.ACT)
        self.assertEqual(result.independent_count, 2)

    def test_duplicate_lineage_cannot_satisfy_independent_quorum(self):
        result = probe([self.item(source="a", group="same"), self.item(source="b", group="same")], "supported", now=self.NOW)
        self.assertEqual(result.decision, Decision.VERIFY)
        self.assertEqual(result.independent_count, 1)

    def test_stale_high_confidence_evidence_cannot_allow_act(self):
        result = probe([self.item(source="a", age=7200), self.item(source="b", age=7300)], "supported", now=self.NOW)
        self.assertEqual(result.decision, Decision.VERIFY)
        self.assertEqual(result.fresh_count, 0)

    def test_fresh_conflicting_claims_escalate(self):
        result = probe([self.item("supported", "a", group="a", claim_key="shipment_status"), self.item("contradicted", "b", group="b", claim_key="shipment_status")], "supported", now=self.NOW)
        self.assertEqual(result.decision, Decision.ESCALATE)
        self.assertTrue(result.conflicting_claims)

    def test_empty_evidence_requests_verification(self):
        result = probe([], "supported", now=self.NOW)
        self.assertEqual(result.decision, Decision.VERIFY)

    def test_confidence_aggregation_must_meet_threshold(self):
        enough = probe([self.item(source="a", confidence=.70, group="a"), self.item(source="b", confidence=.70, group="b")], "supported", now=self.NOW)
        insufficient = probe([self.item(source="a", confidence=.68, group="a"), self.item(source="b", confidence=.68, group="b")], "supported", now=self.NOW)
        self.assertEqual(enough.decision, Decision.ACT)
        self.assertEqual(insufficient.decision, Decision.VERIFY)


if __name__ == "__main__":
    unittest.main()
