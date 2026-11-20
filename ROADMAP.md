# Roadmap

## Immediate — complete the 100-case empirical evaluation

1. Validate all 100 Tier 2 datasets without API calls.
2. Run the two prompt conditions against one frozen provider/model with a real API key.
3. Preserve raw JSON traces, provider/model identifiers, dataset digest, timestamps, latency and failures.
4. Repeat on a second model/provider before making comparative claims.
5. Inspect false blocks and unsafe actions by scenario family, not only aggregate rates.

## Research strengthening

- Add adversarial provenance spoofing and correlated verifier failures.
- Add semantic conflict cases with structured claim fields.
- Add independent human/expert gold-label review for the Tier 2 datasets.
- Add real-world domain adapters that invoke the EXIM and Memory Governor implementations.
- Measure calibration, abstention/verification quality and cost-sensitive trade-offs.
- Keep synthetic conformance, model API results and production integration evidence separate.

## Definition of stronger evidence

A milestone moves from prototype toward a research result only when it has a frozen protocol, documented baselines, repeated runs where randomness exists, inspectable raw traces, an error analysis, and an explicit limitations section.
