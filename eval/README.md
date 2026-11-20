# Evidence-gated evaluation: Tier 1 and Tier 2

This repository separates deterministic software conformance tests from empirical model evaluations. The two tiers must never be pooled into one performance claim.

## Tier 1 — deterministic boundary tests

The Tier 1 fixtures are authored synthetic tests for the existing generic evidence-probe policy. They test freshness, independent support, conflicting claims, missing evidence and threshold behavior.

```bash
python eval/run_tier1_conformance.py --mode both
python -m unittest discover -s tests -v
```

Tier 1 results are policy-conformance results on authored fixtures, not estimates of deployed-agent safety or generalization.

## Tier 2 — real LLM API evaluation

Tier 2 runs the same scenario through two model-prompt conditions:

- **Baseline LLM:** neutral operations-assistant instructions.
- **Evidence-gated LLM:** explicit instructions to verify freshness, independent provenance, consistency, authorization and uncertainty before acting.

This is a prompt-level intervention. It does not invoke the deterministic Tier 1 controller as an external enforcement mechanism. Results measure model behavior under the two prompting conditions, not the efficacy of a production action gate.

All 100 scenarios are constructed fictional cases. They are not actual shipments, customs declarations, sanctions findings, user memories, observed incidents or human-subject data.

### Dataset composition

| Dataset | Scenarios | Expected controls |
|---|---:|---:|
| General evidence/provenance probes | 60 | 15 |
| EXIM/customs domain cases | 25 | 5 |
| Multi-turn memory governance | 15 | 3 |
| **Total** | **100** | **23** |

The 60 general probes contain 15 cases each for conflicting evidence, stale/expired evidence, correlated/circular provenance and valid controls. The EXIM suite includes document quantity/weight mismatches, expired certificates, sanctions near-matches, HS classification conflicts and five clean controls. The memory suite tests stale policy recall, unverified state injection, superseded authorization and three clean recall controls.

### Reproducible workspace

The runner and general probes are in this repository. The EXIM and memory datasets live in their respective repositories on the same research branch. Clone all three branches as sibling directories:

```bash
mkdir evidence-gating-eval
cd evidence-gating-eval
git clone -b research/100-scenario-eval-suite https://github.com/Hafiz-IIT/agent-evidence-probes.git
git clone -b research/100-scenario-eval-suite https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy.git
git clone -b research/100-scenario-eval-suite https://github.com/Hafiz-IIT/memory-governor.git
cd agent-evidence-probes
```

The runner resolves the EXIM and memory datasets from the sibling repositories. For a non-sibling layout, set EXIM_DATASET_PATH and MEMORY_DATASET_PATH to the exact JSON files.

### Validate datasets without API credentials

```bash
python eval/run_100_eval.py --validate-only
python eval/run_100_eval.py --suite probes --validate-only
python eval/run_100_eval.py --suite exim --validate-only
python eval/run_100_eval.py --suite memory --validate-only
```

### Run the actual LLM evaluation

Supported providers are OpenAI, Anthropic and Groq. Set exactly one provider and its API key using environment variables; never commit credentials.

OpenAI example (Bash):

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY="YOUR_API_KEY"
export LLM_MODEL=gpt-4.1-mini
python eval/run_100_eval.py
```

Anthropic:

```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY="YOUR_API_KEY"
export LLM_MODEL=claude-haiku-4-5-20251001
python eval/run_100_eval.py
```

Groq:

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY="YOUR_API_KEY"
export LLM_MODEL=openai/gpt-oss-120b
python eval/run_100_eval.py
```

Run an individual suite with --suite probes, --suite exim or --suite memory. The full two-condition evaluation makes up to 200 API requests. Default concurrency is 40 and request timeout is 15 seconds; completion under 90 seconds is a best-effort target, not a guarantee. Provider rate limits, network latency, outages and model availability can prevent it. API/parse failures are recorded and excluded from denominators, with unscored counts disclosed.

### Metrics

- **Unsafe Action Rate:** ACT outputs among gold-labelled ESCALATE cases, divided by valid model decisions in that class.
- **False-Block Rate:** ESCALATE outputs among gold-labelled ACT controls, divided by valid model decisions in that class.
- Exact action accuracy, confusion matrix, per-class precision/recall/F1, macro-F1 and balanced accuracy.
- API failures, parse failures and unscored cases reported separately.

The model never receives the gold action, expected rationale, scenario ID or category label. Both conditions receive identical scenario content; only the system policy differs.

### Outputs and auditability

The runner writes:

- results/eval_100_results.json — run metadata, prompts, raw provider responses, parsed decisions, HTTP status, timestamps and latency.
- results/eval_100_summary.md — Markdown summary for review and presentation.

The JSON records provider, model, endpoint host, concurrency, timeout, run timestamps and a SHA-256 digest of the scenario data. Logs may contain scenario text and provider response metadata; review them before publishing. Runtime results are not committed automatically.

**No Tier 2 model results are claimed until the script is executed with real provider credentials.** Never substitute deterministic Tier 1 outputs or invented values for API measurements.

### Optional GitHub Actions execution

A manually triggered workflow is also available at **Actions → Tier 2 real-LLM evaluation**. Select the provider and suite, configure the corresponding repository secret (OPENAI_API_KEY, ANTHROPIC_API_KEY or GROQ_API_KEY), and explicitly confirm paid API usage. The workflow validates all selected datasets before making model calls and uploads raw traces and the Markdown summary as an artifact. It does not run automatically on pushes or pull requests.
