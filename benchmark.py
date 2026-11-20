from __future__ import annotations

from dataclasses import dataclass
from agent_evidence_probes import Decision, Evidence, probe


@dataclass(frozen=True)
class Scenario:
    name: str
    target_claim: str
    evidence: tuple[Evidence, ...]
    expected: Decision


def synthetic_scenarios(*, now: float = 1000.0) -> tuple[Scenario, ...]:
    return (
        Scenario(
            "independent_support",
            "valid",
            (
                Evidence("valid", "extractor", 0.95, now, independent_group="model"),
                Evidence("valid", "registry", 0.90, now, independent_group="external"),
            ),
            Decision.ACT,
        ),
        Scenario(
            "single_source",
            "valid",
            (Evidence("valid", "extractor", 0.99, now, independent_group="model"),),
            Decision.VERIFY,
        ),
        Scenario(
            "conflicting_sources",
            "valid",
            (
                Evidence("valid", "registry-A", 0.95, now, independent_group="source-A", claim_key="shipment_status"),
                Evidence("invalid", "registry-B", 0.95, now, independent_group="source-B", claim_key="shipment_status"),
            ),
            Decision.ESCALATE,
        ),
        Scenario(
            "stale_evidence",
            "valid",
            (
                Evidence("valid", "old-registry-A", 0.95, now - 5000, ttl_seconds=100,
                         independent_group="source-A"),
                Evidence("valid", "old-registry-B", 0.95, now - 5000, ttl_seconds=100,
                         independent_group="source-B"),
            ),
            Decision.VERIFY,
        ),
        Scenario(
            "correlated_sources",
            "valid",
            (
                Evidence("valid", "extractor-A", 0.95, now, independent_group="shared-origin"),
                Evidence("valid", "extractor-B", 0.90, now, independent_group="shared-origin"),
            ),
            Decision.VERIFY,
        ),
        Scenario(
            "future_dated_evidence",
            "valid",
            (
                Evidence("valid", "future-A", 0.95, now + 100, independent_group="source-A"),
                Evidence("valid", "current-B", 0.90, now, independent_group="source-B"),
            ),
            Decision.VERIFY,
        ),
    )


def evaluate_scenarios(scenarios: tuple[Scenario, ...], *, now: float) -> dict:
    rows = []
    correct = 0
    for scenario in scenarios:
        result = probe(scenario.evidence, scenario.target_claim, now=now)
        ok = result.decision == scenario.expected
        correct += int(ok)
        rows.append({
            "scenario": scenario.name,
            "expected": scenario.expected.value,
            "actual": result.decision.value,
            "correct": ok,
        })
    unsafe_den = sum(s.expected != Decision.ACT for s in scenarios)
    safe_den = sum(s.expected == Decision.ACT for s in scenarios)
    unsafe = sum(row["expected"] != Decision.ACT and row["actual"] == Decision.ACT.value for row in rows)
    false_blocks = sum(row["expected"] == Decision.ACT.value and row["actual"] != Decision.ACT.value for row in rows)
    return {
        "total": len(rows),
        "correct": correct,
        "accuracy": correct / len(rows) if rows else 0.0,
        "unsafe_actions": unsafe,
        "unsafe_action_denominator": unsafe_den,
        "unsafe_action_rate": unsafe / unsafe_den if unsafe_den else None,
        "false_blocks": false_blocks,
        "valid_control_denominator": safe_den,
        "false_block_rate": false_blocks / safe_den if safe_den else None,
        "rows": rows,
    }
