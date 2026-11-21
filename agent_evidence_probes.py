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


def _finite(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    confidence: float
    observed_at: float
    ttl_seconds: float = 3600.0
    independent_group: str | None = None
    claim_key: str | None = None

    def __post_init__(self):
        for name, value in (("claim", self.claim), ("source", self.source)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        confidence = _finite("confidence", self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        _finite("observed_at", self.observed_at)
        ttl = _finite("ttl_seconds", self.ttl_seconds)
        if ttl < 0:
            raise ValueError("ttl_seconds must be non-negative")
        if self.independent_group is not None and (
            not isinstance(self.independent_group, str) or not self.independent_group.strip()
        ):
            raise ValueError("independent_group must be non-empty when supplied")
        if self.claim_key is not None and (
            not isinstance(self.claim_key, str) or not self.claim_key.strip()
        ):
            raise ValueError("claim_key must be non-empty when supplied")

    def is_fresh(self, now: float | None = None) -> bool:
        now = _finite("now", time.time() if now is None else now)
        # Future-dated evidence is not fresh; it must not pass via a negative age.
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
    value = _finite("confidence", value)
    if not 0.0 <= value <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    return value


def detect_conflicts(evidence: Sequence[Evidence]) -> tuple[str, ...]:
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
        raise ValueError("evidence must be a sequence of Evidence values")
    if any(not isinstance(item, Evidence) for item in evidence):
        raise ValueError("evidence must contain only Evidence values")
    # Different propositions are not contradictions. Only compare claims that
    # explicitly share a caller-defined claim key.
    by_claim_key: dict[str, set[str]] = {}
    for item in evidence:
        if item.claim_key is None:
            continue
        key = item.claim_key.strip().casefold()
        by_claim_key.setdefault(key, set()).add(item.claim.strip().casefold())
    conflicts = {
        f"{key}:{claim}"
        for key, claims in by_claim_key.items()
        if len(claims) > 1
        for claim in claims
    }
    return tuple(sorted(conflicts))


def support_score(evidence: Iterable[Evidence], target_claim: str, now: float | None = None) -> float:
    if not isinstance(target_claim, str) or not target_claim.strip():
        raise ValueError("target_claim must be a non-empty string")
    now = _finite("now", time.time() if now is None else now)
    rows = list(evidence)
    if any(not isinstance(item, Evidence) for item in rows):
        raise ValueError("evidence must contain only Evidence values")
    target = target_claim.strip().casefold()
    usable = [e for e in rows if e.is_fresh(now) and e.claim.strip().casefold() == target]
    if not usable:
        return 0.0
    best_by_group: dict[str, float] = {}
    for item in usable:
        group = item.independent_group or item.source
        best_by_group[group] = max(best_by_group.get(group, 0.0), _normalized_confidence(item.confidence))
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
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
        raise ValueError("evidence must be a sequence of Evidence values")
    if any(not isinstance(item, Evidence) for item in evidence):
        raise ValueError("evidence must contain only Evidence values")
    if not isinstance(target_claim, str) or not target_claim.strip():
        raise ValueError("target_claim must be a non-empty string")
    act_threshold = _finite("act_threshold", act_threshold)
    if not 0.0 <= act_threshold <= 1.0:
        raise ValueError("act_threshold must be between 0 and 1")
    if isinstance(min_independent_sources, bool) or not isinstance(min_independent_sources, int) or min_independent_sources < 1:
        raise ValueError("min_independent_sources must be a positive integer")
    now = _finite("now", time.time() if now is None else now)
    fresh = [e for e in evidence if e.is_fresh(now)]
    matching = [e for e in fresh if e.claim.strip().casefold() == target_claim.strip().casefold()]
    groups = {e.independent_group or e.source for e in matching}
    conflicts = detect_conflicts(fresh)
    score = support_score(fresh, target_claim, now)

    reasons: list[str] = []
    if conflicts: reasons.append("fresh evidence contains conflicting claims")
    if len(groups) < min_independent_sources: reasons.append("insufficient independent support")
    if score < act_threshold: reasons.append("support score below action threshold")
    decision = Decision.ESCALATE if conflicts else (
        Decision.ACT if score >= act_threshold and len(groups) >= min_independent_sources else Decision.VERIFY
    )
    return ProbeResult(decision, round(score, 6), len(fresh), len(groups), conflicts, tuple(reasons))


if __name__ == "__main__":
    now = time.time()
    sample = [
        Evidence("document-valid", "ocr", 0.95, now, independent_group="digital"),
        Evidence("document-valid", "registry", 0.90, now, independent_group="external"),
    ]
    print(probe(sample, "document-valid"))
