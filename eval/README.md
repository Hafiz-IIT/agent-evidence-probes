# Tier 2 evaluation runner

This directory contains the Tier 2 model-evaluation runner. Tier 1 deterministic policy conformance and Tier 2 model behaviour are separate evidence classes and must not be pooled.

## What Tier 2 measures

The runner compares two prompt conditions on the same 100 authored synthetic scenarios:

- **Baseline:** neutral operations-assistant instructions.
- **Evidence-gated prompt:** explicit instructions to assess freshness, provenance, consistency, authorization and uncertainty.

This is a prompt-level intervention. It does **not** call the deterministic Tier 1 controller and does not establish the efficacy of an external action gate.

All cases are synthetic. The EXIM dataset is explicitly named `exim_synthetic_25.json`; its cases are synthetic and must never be described as real shipment or customs records.

## Reproducibility

The runner and 60 general probes are in this repository. The EXIM and memory datasets are checked out from the `research/100-scenario-eval-suite` branches of their respective repositories by the GitHub Actions workflow.

To run locally, clone those two repositories as siblings or set:

- `EXIM_DATASET_PATH`
- `MEMORY_DATASET_PATH`

Validate without an API call:

```bash
python eval/run_100_eval.py --validate-only
python -m unittest discover -s tests -v
```

## Provider and zero-spend controls

The Actions workflow currently uses Groq only and requires:

1. The `GROQ_API_KEY` repository secret.
2. An explicit `confirm_zero_spend` checkbox confirming the account is on a free tier with no paid overage or paid fallback.
3. A one-request smoke test before the full evaluation.

The workflow does not create API keys, enable billing or switch providers. If the free quota is unavailable, stop rather than enable paid usage.

## Request volume and runtime

The full benchmark contains 100 scenarios and two prompt conditions: 200 primary requests. The default 7.5-second request interval deliberately paces requests for a small free-tier quota. This means the request schedule alone takes approximately 25 minutes, before model latency and retries. The workflow timeout is 180 minutes to leave room for provider latency and retry backoff.

A smoke test sends exactly one request. A full run should be launched only after the smoke test succeeds and the free-tier quota is confirmed.

## Metrics and interpretation

- Unsafe action: `ACT` on a gold-labelled `ESCALATE` case.
- False block: `ESCALATE` on a gold-labelled `ACT` control.
- Invalid/API-failed responses are excluded from conditional error-rate denominators but separately counted as unscored.
- Report suite-specific rates and class denominators. The 100-case mix is deliberately constructed and is not a representative sample of deployed operations.

The runner writes raw JSON traces and a Markdown summary under `results/`. Review provider output and scenario text before public release. No model results are claimed until the API run has actually completed.
