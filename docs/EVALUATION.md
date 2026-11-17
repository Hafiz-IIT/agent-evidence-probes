# Evaluation Protocol

## Primary question
When does explicit evidence structure reduce unsafe action authorization compared with confidence-only decision rules?

## Metrics
- Unsafe ACT rate
- Conflict escalation rate
- Independent-source count
- Support-score calibration
- Abstention/verification rate

## Implemented boundary and limitations
- Evidence records and independent-group labels are supplied by the caller.
- This prototype does not authenticate source identities, sign evidence, validate acquisition channels or prove that two groups are operationally independent.
- The lexical conflict detector compares normalized claim keys/text; it does not establish semantic contradiction in arbitrary natural language.
- Freshness is a timestamp/TTL heuristic, not a trusted time service or cryptographic attestation.
- The implementation is a synthetic probe for decision logic, not a production evidence-verification service.

## Minimum experiment standard
1. Freeze the implementation/configuration before evaluation.
2. Run deterministic tests first.
3. Use synthetic or permissioned data only.
4. Report failures and negative results.
5. Separate prototype results from production claims.

## Falsification criteria
- The gate frequently ACTs on conflicting evidence.
- Correlated duplicate sources materially inflate authorization.
- Freshness checks fail to exclude expired or future-dated evidence.
- Caller-supplied independence labels are treated as authenticated proof.

## Reproducibility
```bash
python -m unittest discover -s tests -v
```
