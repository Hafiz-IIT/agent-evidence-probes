# Agent Evidence Probes

> **Research prototype for asking a simple but consequential question: _what evidence actually authorizes an AI agent to act?_**

This repository implements an inspectable evidence-gating layer for agentic systems. It separates **confidence** from **evidence quality** and evaluates freshness, source independence, conflicts, and minimum support before returning one of three outcomes: **ACT**, **VERIFY**, or **ESCALATE**.

## Why this project exists

A multi-stage agent can be internally consistent and still be wrong. Several model outputs may repeat the same underlying source, stale information can look authoritative, and correlated verifiers can create false confidence. This project turns those failure modes into explicit objects that can be tested.

## Implemented

- Evidence records with claim, source, confidence, timestamp, TTL, and independent-source grouping.
- Freshness filtering and expiration.
- Duplicate/correlated-source handling.
- Conflict detection across fresh evidence.
- Saturating support aggregation that does not reward duplicated evidence as independent support.
- Configurable minimum independent sources and action thresholds.
- Structured probe result with decision, evidence counts, conflicts, and reasons.
- Deterministic unit tests and GitHub Actions CI.

## Repository map

| Path | Purpose |
|---|---|
| `agent_evidence_probes.py` | Core evidence model, scoring, conflict detection, and decision gate |
| `tests/` | Deterministic tests for support, duplication, conflicts, and expiry |
| `examples/` | Reproducible synthetic evidence packets |
| `docs/architecture.md` | Architecture and decision flow |
| `docs/research-agenda.md` | Research questions, falsification criteria, and paper lineage |
| `STATUS.md` | What is implemented vs. what is not claimed |
| `CITATION.cff` | Software citation metadata |
| `NOTICE.md` | Research/portfolio use notice |

## Quick start

```bash
python -m unittest discover -s tests -v
python agent_evidence_probes.py
```

Python 3.11+ is sufficient; the current implementation has no third-party runtime dependencies.

## Minimal example

```python
import time
from agent_evidence_probes import Evidence, probe

now = time.time()
packet = [
    Evidence("document-valid", "extractor", 0.95, now, independent_group="model"),
    Evidence("document-valid", "registry", 0.90, now, independent_group="external"),
]

result = probe(packet, "document-valid")
print(result.decision, result.support_score)
```

## Research lineage

This repository belongs to a longer research direction on **evidence-gated autonomy, verifier co-failure, correlated evidence, provenance, and human escalation**. It also connects to the historical paper directions **“Scalable Architectures for Distributed Intelligent Agents”** and **“Ethical and Legal Dimensions of Autonomous Systems.”** Those titles are research directions from earlier project planning; they are **not represented here as published papers**.

## Evaluation philosophy

A useful benchmark should be able to make this method fail. Planned stressors therefore include:

1. correlated sources masquerading as independent evidence;
2. stale evidence with high confidence;
3. mutually consistent but jointly wrong evidence;
4. spoofed provenance or independence metadata;
5. asymmetric cost of false ACT vs. unnecessary escalation.

See `docs/research-agenda.md` for proposed experiments.

## Current status

**Maturity: reproducible research prototype.**

The code and deterministic tests are implemented. The repository does **not** claim production deployment, real-world agent-safety guarantees, formal verification, or external-LLM evaluation.

## Related portfolio work

- `EXIM-AI-Evidence-Gated-Autonomy` — broader evidence-gated autonomy experiments.
- `exim-document-truth-bench` — cross-document truth/consistency failures.
- `memory-governor` — persistent memory governance and stale-memory control.
- `hafs-os-core` — task authority, risk, permissions, and evidence requirements.
