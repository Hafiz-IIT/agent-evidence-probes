# Tier 2 empirical LLM evaluation

This runner compares two model-prompt conditions over three constructed scenario datasets:

- probes: 60 evidence/provenance scenarios
- exim: 25 fictional EXIM/customs scenarios
- memory: 15 fictional multi-turn memory/authorization scenarios

The 100 fixtures are synthetic and do not represent real shipments, customs cases, users, memories, or observed incidents. The model responses are empirical API outputs only when you run the script with your own provider credentials.

## Workspace layout

Clone these three repositories as sibling directories:

    workspace/
      agent-evidence-probes/
      EXIM-AI-Evidence-Gated-Autonomy/
      memory-governor/

Run the script from agent-evidence-probes. The runner reads the EXIM and memory datasets from the sibling repositories. If the sibling repositories are not present, those suites cannot be loaded.

## Run

Set one provider and its API key in your shell:

    set LLM_PROVIDER=openai
    set OPENAI_API_KEY=...

Then run:

    python eval/run_100_eval.py
    python eval/run_100_eval.py --suite probes
    python eval/run_100_eval.py --suite exim memory
    python eval/run_100_eval.py --concurrency 40 --timeout 15

Supported providers are OpenAI, Anthropic and Groq. Override the model with LLM_MODEL and the endpoint with LLM_BASE_URL if required. Never commit API keys.

The default concurrency and per-request timeout are sized for a best-effort run under 90 seconds. External API latency, rate limits, provider outages and retries can still affect elapsed time; the runner does not claim a hard real-time guarantee.

## Conditions and metrics

- Baseline: the model receives a neutral operations-assistant instruction.
- Evidence-gated: the model receives an explicit evidence-checking policy in its system prompt.
- The evidence-gated condition is prompt-level only. It does not invoke the repository's deterministic Tier 1 controller or prove that the controller improves real-world model behaviour.
- Unsafe action rate: ACT outputs among gold-labelled ESCALATE cases, divided by valid model decisions in that class.
- False-block rate: ESCALATE outputs among gold-labelled ACT controls, divided by valid model decisions in that class.
- API and parse failures are reported separately, including unscored cases in each gold class. They are not silently counted as safe decisions or allowed to dilute either rate.

Tier 1 deterministic synthetic tests remain separate. Do not pool Tier 1 and Tier 2 metrics.

## Outputs

The runner writes:

- results/eval_100_results.json — complete request/response traces and metadata
- results/eval_100_summary.md — Markdown table for review

Review the traces for provider errors, invalid responses, model/version changes and unexpected prompt leakage before publishing results. These files are runtime outputs and are ignored by Git by default.

No API call results are included in the repository until a user runs the evaluation with valid credentials. Do not invent or pre-fill metrics.
