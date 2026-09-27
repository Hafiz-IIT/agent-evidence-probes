# Research agenda

## Central question

**What evidence should an autonomous system require before it is allowed to take a consequential action?**

## Testable hypotheses

### H1 — independence helps
For the same marginal verifier quality, evidence aggregated across genuinely independent sources should reduce incorrect ACT decisions relative to duplicated/correlated sources.

**Falsification:** no measurable reduction in incorrect ACT rate under controlled correlation.

### H2 — confidence-only authorization is brittle
A policy based only on model confidence should fail more often under stale, correlated, or provenance-corrupted evidence than a policy with explicit evidence checks.

**Falsification:** confidence-only performs equivalently across the stress regimes.

### H3 — provenance is a trust root
Benefits from evidence gating should collapse when provenance/independence labels can be spoofed.

**Falsification:** spoofing does not materially change unsafe-action rate.

## Proposed experiment matrix

| Regime | Freshness | Source correlation | Conflicts | Provenance |
|---|---:|---:|---:|---|
| clean | fresh | independent | none | trusted |
| stale | mixed | independent | none | trusted |
| correlated | fresh | high | none | trusted |
| conflict | fresh | mixed | present | trusted |
| spoofed | fresh | hidden correlation | optional | untrusted |
| compound | mixed | high | present | untrusted |

Primary metrics: incorrect consequential action rate, escalation rate, verification burden, and coverage.

## Historical paper lineage

Earlier project planning included the titles:

- **Scalable Architectures for Distributed Intelligent Agents**
- **Ethical and Legal Dimensions of Autonomous Systems**

They are preserved here as historical research directions, not publication claims.

## Publication rule

A paper should only be promoted from “candidate direction” after this repository has:

1. a frozen benchmark;
2. reproducible experiment scripts;
3. baselines;
4. results with uncertainty;
5. negative/failure analysis;
6. a limitations section.
