# Status

## Implemented

- Generic evidence probe with freshness, TTL, conflict and independent-group checks.
- Strict evidence input validation and future-timestamp rejection.
- Tier 1 deterministic conformance runner and 100 synthetic cases.
- Tier 2 100-scenario real-LLM runner across general evidence, EXIM and memory domains.
- OpenAI, Anthropic and Groq provider adapters.
- Prompt blinding for scenario IDs, categories, gold actions and rationales.
- Unsafe-action and false-block metrics, confusion matrix, macro-F1, balanced accuracy, and explicit API/parse failures.
- Dataset validation without API credentials.
- CI for unit tests, Tier 1 execution and Tier 2 dataset validation.

## Not yet claimed

- Real Tier 2 model results (no provider API key used).
- Cryptographic authentication of source identity or independence.
- Semantic contradiction detection.
- Production enforcement or deployment safety.
- Generalization to real customs, shipment, or memory records.
- Human-subject or native-expert validation.

## Research boundary

Tier 1 is deterministic software conformance on authored synthetic fixtures. Tier 2 is a planned empirical comparison of real LLM API responses on constructed fictional scenarios. The Tier 2 evidence-gated condition changes the model prompt; it does not wrap the model in an external deterministic controller.
