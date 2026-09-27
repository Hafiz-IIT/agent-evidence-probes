# Project status

## Implemented and inspectable

- Core `Evidence` and `ProbeResult` data structures.
- Freshness/TTL checks.
- Conflict detection.
- Independent-source grouping.
- Saturating confidence aggregation.
- ACT / VERIFY / ESCALATE decision gate.
- Unit tests.
- GitHub Actions unit-test workflow.
- Synthetic example packet.

## Research-stage / not yet implemented

- Cryptographic provenance or hardware-backed attestation.
- Learned verifier ensembles.
- Real LLM/API traces.
- Adversarial provenance-spoofing benchmark.
- Human-subject escalation study.
- Calibrated cost-sensitive policy learning.
- Production authentication, storage, or observability.

## Claims boundary

This repository demonstrates a **mechanism and test scaffold**. It does not establish that evidence gating “solves” agent safety, nor that source labels supplied to the gate are themselves trustworthy.

## Version

Current public prototype line: **0.1.x**.
