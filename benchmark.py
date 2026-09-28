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
    return {
        "total": len(rows),
        "correct": correct,
        "accuracy": correct / len(rows) if rows else 0.0,
        "rows": rows,
    }
