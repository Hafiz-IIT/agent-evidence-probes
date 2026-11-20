# Portfolio Audit Matrix — Current Index

**Scope:** 33 project repositories. The GitHub profile README is excluded from review and edits. Repository READMEs may be used to identify project purpose; no profile README content is included.

The canonical portfolio inventory, research-maturity boundaries, confirmed defects, repairs, and CI evidence are maintained in:

[GitHub Portfolio Deep Audit — 2026-11-18](https://github.com/Hafiz-IIT/hafs-os-core/blob/audit/permissioned-evidence-and-atomic-graph/docs/PORTFOLIO_DEEP_AUDIT_2026-11-18.md)

## Current high-priority research repositories

| Repository | Purpose | Current validation branch |
|---|---|---|
| agent-evidence-probes | Generic evidence-gating policy and Tier 1/Tier 2 evaluation | [PR #6](https://github.com/Hafiz-IIT/agent-evidence-probes/pull/6) |
| EXIM-AI-Evidence-Gated-Autonomy | EXIM document evidence, provenance, witness independence and action authorization | [PR #16](https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy/pull/16) |
| memory-governor | Memory provenance, scope, retention, sensitivity and supersession | [PR #5](https://github.com/Hafiz-IIT/memory-governor/pull/5) |

## Evidence labels

- **CI green:** configured checks passed at the recorded commit.
- **Synthetic conformance:** deterministic policy behavior on authored fixtures.
- **Empirical model evaluation:** actual provider API responses with raw traces; not yet run for Tier 2.
- **Research protocol:** a manuscript or experiment design that still needs execution.
- **Externally validated:** requires independent replication or real-world validation; not claimed by this audit.

Do not interpret CI green or synthetic conformance as evidence of deployed-agent safety.
