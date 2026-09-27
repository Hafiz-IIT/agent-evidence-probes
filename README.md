# Agent Evidence Probes

A small research-oriented toolkit for testing whether an AI-agent decision is supported by sufficient, independent, and non-conflicting evidence.

## Why this exists

Agentic systems can sound confident while relying on stale, circular, weak, or mutually inconsistent evidence. This repository isolates that problem and makes it measurable.

## Implemented

- evidence items with provenance, freshness and confidence
- conflict detection across evidence claims
- source-independence checks
- weighted support scoring
- decision probes that return **ACT / VERIFY / ESCALATE**
- deterministic tests for supported, conflicting and under-evidenced cases

## Quick start

```bash
python -m unittest discover -s tests -v
python agent_evidence_probes.py
```

## Research status

This is a reproducible prototype and evaluation scaffold, not a claim of production-grade agent safety. It uses synthetic evidence objects and deterministic rules so failure modes are inspectable.

## Related work

This repository extends the broader evidence-gated autonomy direction in my EXIM and agent-safety work: before a consequential action, ask what evidence supports it, whether that evidence is independent, whether it conflicts, and whether a human should receive the case instead.
