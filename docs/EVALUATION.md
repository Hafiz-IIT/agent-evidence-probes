# Evaluation Protocol

## Primary question
When does explicit evidence structure reduce unsafe action authorization compared with confidence-only decision rules?

## Metrics
- Unsafe ACT rate
- Conflict escalation rate
- Independent-source count
- Support-score calibration
- Abstention/verification rate

## Minimum experiment standard
1. Freeze the implementation/configuration before evaluation.
2. Run deterministic tests first.
3. Use synthetic or permissioned data only.
4. Report failures and negative results.
5. Separate prototype results from production claims.

## Falsification criteria
- The gate frequently ACTs on conflicting evidence.
- Correlated duplicate sources materially inflate authorization.
- Freshness checks fail to exclude expired evidence.

## Reproducibility
The default CI command is:
```bash
python -m unittest discover -s tests -v
```
