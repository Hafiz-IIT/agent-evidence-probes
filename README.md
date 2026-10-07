# Agent Evidence Probes

<p align="center">
  <strong>Evidence-Gated Autonomy for AI Agents</strong><br/>
  <sub>Testing whether an agent has enough fresh, independent evidence to act.</sub>
</p>

<p align="center">
  <a href="https://github.com/Hafiz-IIT/agent-evidence-probes/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hafiz-IIT/agent-evidence-probes/ci.yml?label=CI" alt="CI"/></a>
  <img src="https://img.shields.io/badge/status-research%20prototype-blue" alt="Research prototype"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT"/>
</p>

## Research question

**When should an autonomous system trust its evidence enough to act—and when should it verify or escalate?**

This lab turns that question into executable probes around **freshness, provenance, independence, conflict and evidence sufficiency**.

## The decision loop

```
Evidence
   ↓
Freshness + provenance
   ↓
Independence / conflict analysis
   ↓
Support threshold
   ↓
ACT ── VERIFY ── ESCALATE
```

The key design choice is that *more evidence is not automatically better evidence*: correlated or stale sources can create false confidence.

## Try it

```bash
python agent_evidence_probes.py
python -m unittest discover -s tests -v
```

The repository also contains `benchmark.py`, a deterministic reference benchmark covering supported, stale, conflicting and insufficient-evidence cases.

## What is actually implemented

- evidence objects with source/provenance metadata
- freshness filtering
- source-independence grouping
- conflict detection
- support aggregation
- explicit ACT / VERIFY / ESCALATE outcomes
- reproducible benchmark cases
- automated CI

## Research boundary

This is a **research prototype**, not a claim about production agent safety or empirical validation on deployed agents.

## Why it matters

This project is one component of a broader research direction: **making autonomous systems evidence-aware before they receive authority to act**.

Related work: [Memory Governor](https://github.com/Hafiz-IIT/memory-governor) · [Safe RL Action Gate](https://github.com/Hafiz-IIT/safe-rl-action-gate) · [~haf.s__ OS Core](https://github.com/Hafiz-IIT/hafs-os-core)

## Reproducibility

The tests are deterministic and run in GitHub Actions. Start with `tests/` and `docs/ARCHITECTURE.md` for the implementation-level specification.
