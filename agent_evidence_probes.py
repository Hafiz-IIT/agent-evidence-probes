from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence
import math
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
    claim_key: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.claim, str) or not self.claim.strip():
            raise ValueError("claim must be a non-empty string")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not math.isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be finite and within [0, 1]")
        if not math.isfinite(self.observed_at):
            raise ValueError("observed_at must be finite")
        if not math.isfinite(self.ttl_seconds) or self.ttl_seconds < 0:
            raise ValueError("ttl_seconds must be finite and non-negative")
        if self.independent_group is not None and not self.independent_group.strip():
            raise ValueError("independent_group cannot be empty")
        if self.claim_key is not None and not self.claim_key.strip():
            raise ValueError("claim_key cannot be empty")

    def is_fresh(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if not math.isfinite(now):
            raise ValueError("now must be finite")
        age = now - self.observed_at
        return 0.0 <= age <= self.ttl_seconds


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
    # Different propositions are not contradictions. Only compare values that
    # explicitly refer to the same caller-defined claim key.
    by_claim_key: dict[str, set[str]] = {}
    for item in evidence:
        if item.claim_key is None:
            continue
        key = item.claim_key.strip().lower()
        by_claim_key.setdefault(key, set()).add(item.claim.strip().lower())

    conflicts = {
        f"{key}:{claim}"
        for key, claims in by_claim_key.items()
        if len(claims) > 1
        for claim in claims
    }
    return tuple(sorted(conflicts))


def support_score(evidence: Iterable[Evidence], target_claim: str, now: float | None = None) -> float:
    now = time.time() if now is None else now
    if not math.isfinite(now) or not isinstance(target_claim, str) or not target_claim.strip():
        raise ValueError("now must be finite and target_claim must be non-empty")
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
    if not math.isfinite(now):
        raise ValueError("now must be finite")
    if not isinstance(target_claim, str) or not target_claim.strip():
        raise ValueError("target_claim must be non-empty")
    if not math.isfinite(act_threshold) or not 0.0 <= act_threshold <= 1.0:
        raise ValueError("act_threshold must be finite and within [0, 1]")
    if not isinstance(min_independent_sources, int) or isinstance(min_independent_sources, bool) or min_independent_sources < 1:
        raise ValueError("min_independent_sources must be a positive integer")
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
