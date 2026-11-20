# Evaluation protocol

## Scope and evidence levels

The central suite combines three authored synthetic datasets:

- `data/probes_60.json` — 60 general evidence-gating scenarios.
- `data/exim_real_25.json` — 25 EXIM-context scenarios.
- `data/memory_15.json` — 15 memory-governance-context scenarios.

All 100 cases are synthetic. The EXIM and memory cases are contextual examples, not actual shipment records, customs documents, customer data, or user memories. The central runner invokes only the generic `agent_evidence_probes.probe()` policy. It does **not** invoke the EXIM application policy engine, cryptographic attestation implementation, or Memory Governor production code. Domain-specific behavior must be evaluated by their own repository tests and integration adapters before claiming end-to-end domain coverage.

Each scenario declares an `evaluation_mechanism`. The loader validates that the evidence fixture represents that mechanism and that the expected action is structurally consistent:

- `fresh_independent_support`: fresh corroborating claims from at least two independent lineages.
- `missing_evidence`: no evidence supplied.
- `stale_evidence`: all supplied evidence exceeds its TTL.
- `weak_independent_support`: independent evidence whose aggregate support is below the action threshold.
- `dependent_sources`: multiple records from one lineage only.
- `single_source_support`: one lineage only.
- `fresh_conflicting_claims`: fresh evidence contains incompatible claims.

## Tier 1 deterministic evaluation

Run both comparators:

```bash
python eval/run_100_eval.py --mode both
```

The baseline is confidence-only: ACT if any evidence item has confidence >= 0.90, otherwise VERIFY. It deliberately ignores freshness, provenance, independence and conflicts.

The evidence-gated comparator calls the repository's existing `probe()` implementation, which checks freshness, independent support, conflicts and the action threshold.

The expected labels and fixtures are authored together. Tier 1 therefore measures deterministic policy conformance on this designed test set; it is not independent empirical evidence of deployed-agent safety or generalization.

## Metrics

The runner reports unsafe action rate, false-block rate, exact action accuracy, an ACT / VERIFY / ESCALATE confusion matrix, per-class precision/recall/F1, macro-F1 and balanced accuracy. Every rate includes its numerator and denominator. Undefined denominators are `null`, not zero.

## Tier 2 model evaluation

The runner can submit scenarios to an OpenAI-compatible Chat Completions endpoint. Supply credentials through environment variables; never commit them.

PowerShell example:

```powershell
$env:EVAL_API_KEY = "YOUR_API_KEY"
$env:EVAL_MODEL = "gpt-4.1-mini"
$env:EVAL_API_BASE_URL = "https://api.openai.com/v1"
python eval/run_100_eval.py --mode llm-both --concurrency 5
```

For another compatible provider, set `EVAL_API_BASE_URL` and `EVAL_MODEL`. Tier 2 requires an explicitly supplied API key and may incur provider usage. It has not been run by the deterministic CI workflow.

## Reproducibility

Each run writes timestamped JSON, CSV and Markdown outputs under `results/`. The GitHub Actions workflow runs the deterministic comparison on pull requests and uploads the outputs as an artifact. Preserve the run timestamp, commit SHA, model identifier, endpoint, prompt, API configuration and raw outputs when conducting Tier 2.

A perfect Tier 1 score means only that the tested implementation conforms to the authored expected labels. Do not present it as a real-world safety rate, causal performance estimate, or validation of domain-specific subsystems.
