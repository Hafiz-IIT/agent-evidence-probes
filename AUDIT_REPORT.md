# Agent Evidence Probes — Technical Audit

## Current scope

This repository contains a generic evidence-gating policy, deterministic Tier 1 conformance fixtures, and a Tier 2 real-LLM evaluation harness shared with the EXIM Autonomy and Memory Governor repositories.

## Repairs in this branch

- Reject malformed evidence values and future-dated observations.
- Keep Tier 1 deterministic execution separate from Tier 2 API evaluation.
- Add 60 Tier 2 synthetic probes: 15 conflicting, 15 stale/expired, 15 correlated/circular-provenance, and 15 valid controls.
- Add OpenAI, Anthropic and Groq API support with asynchronous batching.
- Hide scenario IDs, categories, gold actions and expected rationales from model prompts.
- Record provider/model metadata, prompts, raw responses, timestamps, latency, HTTP status, and dataset digest.
- Report unsafe-action rate and false-block rate with denominators and failures separately.
- Preserve Tier 1 results and Tier 2 traces as different evidence classes.
- Document that caller-supplied independence groups are not cryptographic proof of independent origin.

## Validation

Latest completed run on the unified research branch:

- [Unit tests](https://github.com/Hafiz-IIT/agent-evidence-probes/actions/runs/44798970959) — passed.
- [Tier 1 deterministic evaluation](https://github.com/Hafiz-IIT/agent-evidence-probes/actions/runs/44798970852) — passed.
- [Tier 2 100-case dataset validation](https://github.com/Hafiz-IIT/agent-evidence-probes/actions/runs/44798970734) — passed.
- [CI](https://github.com/Hafiz-IIT/agent-evidence-probes/actions/runs/44798970896) — passed.

The Tier 1 benchmark is an authored synthetic conformance set. Its perfect evidence-gated score is expected because fixture construction follows the policy's explicit rules. It is not independent empirical validation or a real-world safety rate.

## Tier 2 execution status

The real-LLM runner is implemented, but no provider API call has been made in this branch because no API credential was supplied. Therefore there are **no Tier 2 model results** to report. Run it with a real provider key using the instructions in eval/README.md.

## Remaining limitations

- Evidence freshness, confidence, and lineage are supplied by the caller; the prototype does not authenticate them.
- Conflict detection is claim-level and not semantic verification.
- The Tier 2 comparison is a prompt-level intervention, not an external deterministic action controller.
- All 100 Tier 2 scenarios are fictional, authored test cases, not observed incidents or records.
- A model API run does not establish deployment safety or generalization beyond the constructed test distribution.

## Reproduction

```bash
python -m unittest discover -s tests -v
python eval/run_tier1_conformance.py --mode both
python eval/run_100_eval.py --validate-only
```
