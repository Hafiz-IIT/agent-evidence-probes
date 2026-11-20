# Tier 2 empirical LLM evaluation

This runner compares two model-prompt conditions over three constructed scenario datasets:

- probes: 60 evidence/provenance scenarios
- exim: 25 fictional EXIM/customs scenarios
- memory: 15 fictional multi-turn memory/authorization scenarios

The 100 fixtures are synthetic and do not represent real shipments, customs cases, users, memories, or observed incidents. Model responses are empirical API outputs only after you run the script with your own provider credentials.

## Reproducible workspace setup

The datasets live on draft research branches in their respective repositories. Clone those exact branches as sibling directories:

    mkdir ega-tier2-workspace
    cd ega-tier2-workspace
    git clone -b research/real-world-100-eval https://github.com/Hafiz-IIT/agent-evidence-probes.git
    git clone -b research/tier2-exim-empirical-suite https://github.com/Hafiz-IIT/EXIM-AI-Evidence-Gated-Autonomy.git
    git clone -b research/tier2-memory-empirical-suite https://github.com/Hafiz-IIT/memory-governor.git

The runner is in agent-evidence-probes. Do not substitute the default branches until these dataset changes are merged or otherwise made available there.

## Run

From the workspace root, set one provider and its API key in your shell, then execute:

    cd agent-evidence-probes
    set LLM_PROVIDER=openai
    set OPENAI_API_KEY=...

    python eval/run_100_eval.py
    python eval/run_100_eval.py --suite probes
    python eval/run_100_eval.py --suite exim memory
    python eval/run_100_eval.py --concurrency 40 --timeout 15

Supported providers are OpenAI, Anthropic and Groq. Override the model with LLM_MODEL and the endpoint with LLM_BASE_URL if required. Never commit API keys.

The default concurrency and per-request timeout are sized for a best-effort run under 90 seconds: 200 requests for the full 100-scenario, two-mode evaluation are dispatched with concurrency 40 and a 15-second per-request timeout. External API latency, provider rate limits, outages and network conditions can still affect elapsed time; this is not a hard real-time guarantee.

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

The JSON includes prompts, raw provider responses, timestamps, latency, model metadata and parsed decisions. Treat these logs as potentially sensitive because they contain scenario text and provider response metadata. Review them before publishing. Runtime outputs are ignored by Git by default.

No API call results are included in the repository until a user runs the evaluation with valid credentials. Do not invent or pre-fill metrics.
