from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence
import time


class Decision(str, Enum):
    ACT = "ACT"
    VERIFY = "VERIFY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    confidence: float
    observed_at: float
    ttl_seconds: float = 3600.0
    independent_group: str | None = None

    def is_fresh(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        return now - self.observed_at <= self.ttl_seconds


@dataclass(frozen=True)
class ProbeResult:
    decision: Decision
    support_score: float
    fresh_count: int
    independent_count: int
    conflicting_claims: tuple[str, ...]
    reasons: tuple[str, ...]


def _normalized_confidence(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def detect_conflicts(evidence: Sequence[Evidence]) -> tuple[str, ...]:
    by_source: dict[str, set[str]] = {}
    for item in evidence:
        by_source.setdefault(item.independent_group or item.source, set()).add(item.claim.strip().lower())

    all_claims = sorted({claim for claims in by_source.values() for claim in claims})
    return tuple(all_claims) if len(all_claims) > 1 else ()


def support_score(evidence: Iterable[Evidence], target_claim: str, now: float | None = None) -> float:
    now = time.time() if now is None else now
    target = target_claim.strip().lower()
    usable = [
        e for e in evidence
        if e.is_fresh(now) and e.claim.strip().lower() == target
    ]
    if not usable:
        return 0.0

    best_by_group: dict[str, float] = {}
    for item in usable:
        group = item.independent_group or item.source
        best_by_group[group] = max(best_by_group.get(group, 0.0), _normalized_confidence(item.confidence))

    # Saturating aggregation: extra independent evidence helps, duplicate evidence does not.
    remaining_risk = 1.0
    for confidence in best_by_group.values():
        remaining_risk *= 1.0 - confidence
    return 1.0 - remaining_risk


def probe(
    evidence: Sequence[Evidence],
    target_claim: str,
    *,
    act_threshold: float = 0.90,
    min_independent_sources: int = 2,
    now: float | None = None,
) -> ProbeResult:
    now = time.time() if now is None else now
    fresh = [e for e in evidence if e.is_fresh(now)]
    matching = [e for e in fresh if e.claim.strip().lower() == target_claim.strip().lower()]
    groups = {e.independent_group or e.source for e in matching}
    conflicts = detect_conflicts(fresh)
    score = support_score(fresh, target_claim, now)

    reasons: list[str] = []
    if conflicts:
        reasons.append("fresh evidence contains conflicting claims")
    if len(groups) < min_independent_sources:
        reasons.append("insufficient independent support")
    if score < act_threshold:
        reasons.append("support score below action threshold")

    if conflicts:
        decision = Decision.ESCALATE
    elif score >= act_threshold and len(groups) >= min_independent_sources:
        decision = Decision.ACT
    else:
        decision = Decision.VERIFY

    return ProbeResult(
        decision=decision,
        support_score=round(score, 6),
        fresh_count=len(fresh),
        independent_count=len(groups),
        conflicting_claims=conflicts,
        reasons=tuple(reasons),
    )


if __name__ == "__main__":
    now = time.time()
    sample = [
        Evidence("document-valid", "ocr", 0.95, now, independent_group="digital"),
        Evidence("document-valid", "registry", 0.90, now, independent_group="external"),
    ]
    print(probe(sample, "document-valid"))
