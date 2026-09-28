# Agent Evidence Probes

> Research toolkit for testing whether autonomous-agent actions are supported by fresh, independent, non-conflicting evidence.

## Status
**Reproducible research prototype.** The repository contains executable Python, deterministic tests, and GitHub Actions CI. It does not claim production deployment or external validation.

## Problem
Agentic systems may authorize consequential actions from stale, circular, weak, or mutually inconsistent evidence. This project makes those failure modes explicit and testable.

## Architecture
Evidence objects → freshness filtering → provenance/independence grouping → conflict detection → support aggregation → ACT / VERIFY / ESCALATE.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component responsibilities and invariants.

## Quick start
```bash
python -m unittest discover -s tests -v
python agent_evidence_probes.py
```

## What is implemented
- Evidence records with provenance groups and TTL
- Conflict detection
- Independent-source counting
- Saturating support aggregation
- ACT / VERIFY / ESCALATE decision probe
- Deterministic tests and CI

## Evaluation
Synthetic scenarios measure unsafe authorization, conflict handling, evidence independence, and abstention/escalation behavior.

See [docs/EVALUATION.md](docs/EVALUATION.md) for the protocol and falsification criteria.

## Research lineage
This repo is grounded in the recovered long-running research/project discussions and maps to:
- *Scalable Architectures for Distributed Intelligent Agents*
- *Ethical & Legal Dimensions of Autonomous Systems*
- *Human–AI Symbiosis for Future Systems*

See [docs/RESEARCH_CONTEXT.md](docs/RESEARCH_CONTEXT.md).

## Repository structure
- `agent_evidence_probes.py` — executable core
- `tests/` — deterministic regression tests
- `docs/` — architecture, research context, evaluation
- `ROADMAP.md` — next experiments and engineering milestones
- `CITATION.cff` — citation metadata
- `.github/workflows/tests.yml` — CI

## Limitations
- Synthetic evidence only
- No claim of formal safety guarantee
- No trusted hardware attestation yet
- Heuristic support aggregation is intentionally simple

## License
MIT. See [LICENSE](LICENSE).
