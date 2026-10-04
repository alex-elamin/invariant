from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True, slots=True)
class Claim:
    text: str
    expected_direction: str = "negative"

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("claim text cannot be empty")
        if self.expected_direction not in {"negative", "positive"}:
            raise ValueError("expected_direction must be 'negative' or 'positive'")


@dataclass(frozen=True, slots=True)
class AnalysisSpecification:
    churn_days: int
    min_orders: int

    def __post_init__(self) -> None:
        if self.churn_days <= 0:
            raise ValueError("churn_days must be > 0")
        if self.min_orders <= 0:
            raise ValueError("min_orders must be > 0")

    def canonical_dict(self) -> dict[str, int]:
        return {"churn_days": self.churn_days, "min_orders": self.min_orders}

    @property
    def variant_id(self) -> str:
        payload = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True, slots=True)
class DecisionSpace:
    churn_days: tuple[int, ...]
    min_orders: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.churn_days or not self.min_orders:
            raise ValueError("decision-space dimensions cannot be empty")
        if any(value <= 0 for value in (*self.churn_days, *self.min_orders)):
            raise ValueError("decision-space values must be > 0")


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    variant_id: str
    specification: AnalysisSpecification
    discount_customers: int
    no_discount_customers: int
    discount_churn_rate: float
    no_discount_churn_rate: float
    effect: float
    direction: str
    sql: str
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["specification"] = self.specification.canonical_dict()
        return value


@dataclass(frozen=True, slots=True)
class MagnitudePolicy:
    """Policy for deciding whether an effect remains materially comparable."""

    minimum_effect: float = 0.01
    retention_ratio: float = 0.50

    def __post_init__(self) -> None:
        if self.minimum_effect < 0:
            raise ValueError("minimum_effect must be >= 0")
        if not 0 < self.retention_ratio <= 1:
            raise ValueError("retention_ratio must be in (0, 1]")


@dataclass(frozen=True, slots=True)
class SensitivityResult:
    dimension: str
    changed_variants: int
    disagreement_rate: float
    magnitude_failure_rate: float | None = None
    median_absolute_effect_delta: float | None = None


@dataclass(frozen=True, slots=True)
class RobustnessReport:
    claim: Claim
    original: AnalysisResult
    results: tuple[AnalysisResult, ...]
    direction_stability: float
    direction_counts: dict[str, int]
    magnitude_stability: float | None
    magnitude_threshold: float | None
    magnitude_policy: MagnitudePolicy
    sensitivity: tuple[SensitivityResult, ...]

    @property
    def assessment(self) -> str:
        if self.original.direction == "neutral":
            return "INDETERMINATE_BASELINE"
        if self.direction_stability < 1.0:
            return "DIRECTION_FRAGILE"
        if self.magnitude_stability is not None and self.magnitude_stability < 1.0:
            return "MAGNITUDE_FRAGILE"
        return "ROBUST_WITHIN_TESTED_SPACE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": asdict(self.claim),
            "original": self.original.to_dict(),
            "summary": {
                "variants_executed": len(self.results),
                "direction_stability": self.direction_stability,
                "direction_counts": self.direction_counts,
                "magnitude_stability": self.magnitude_stability,
                "magnitude_threshold": self.magnitude_threshold,
                "magnitude_policy": asdict(self.magnitude_policy),
                "assessment": self.assessment,
            },
            "sensitivity": [asdict(item) for item in self.sensitivity],
            "results": [result.to_dict() for result in self.results],
        }
