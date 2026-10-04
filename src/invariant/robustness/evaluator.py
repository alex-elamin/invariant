from __future__ import annotations

from statistics import median

from invariant.core.models import (
    AnalysisSpecification,
    Claim,
    MagnitudePolicy,
    RobustnessReport,
    SensitivityResult,
)
from invariant.execution.base import AnalysisExecutor


def _changed_dimensions(original: AnalysisSpecification, candidate: AnalysisSpecification) -> tuple[str, ...]:
    dimensions: list[str] = []
    if original.churn_days != candidate.churn_days:
        dimensions.append("churn_days")
    if original.min_orders != candidate.min_orders:
        dimensions.append("min_orders")
    return tuple(dimensions)


class RobustnessEvaluator:
    def __init__(self, executor: AnalysisExecutor, magnitude_policy: MagnitudePolicy | None = None) -> None:
        self.executor = executor
        self.magnitude_policy = magnitude_policy or MagnitudePolicy()

    def evaluate(self, claim: Claim, original_specification: AnalysisSpecification, variants: tuple[AnalysisSpecification, ...]) -> RobustnessReport:
        by_id = {item.variant_id: item for item in variants}
        by_id[original_specification.variant_id] = original_specification
        ordered_specs = tuple(by_id[key] for key in sorted(by_id))
        results = tuple(self.executor.execute(specification) for specification in ordered_specs)
        original = {result.variant_id: result for result in results}[original_specification.variant_id]

        same_direction = sum(result.direction == original.direction for result in results)
        direction_stability = same_direction / len(results)
        direction_counts = {direction: sum(result.direction == direction for result in results) for direction in ("negative", "neutral", "positive")}

        if abs(original.effect) < self.magnitude_policy.minimum_effect:
            magnitude_threshold = None
            magnitude_stability = None
        else:
            magnitude_threshold = max(self.magnitude_policy.minimum_effect, abs(original.effect) * self.magnitude_policy.retention_ratio)
            magnitude_stability = sum(abs(result.effect) >= magnitude_threshold for result in results) / len(results)

        sensitivity: list[SensitivityResult] = []
        for dimension in ("churn_days", "min_orders"):
            changed = [result for result in results if dimension in _changed_dimensions(original_specification, result.specification)]
            disagreement_rate = sum(result.direction != original.direction for result in changed) / len(changed) if changed else 0.0
            magnitude_failure_rate = (sum(abs(result.effect) < magnitude_threshold for result in changed) / len(changed) if changed and magnitude_threshold is not None else None)
            deltas = [abs(result.effect - original.effect) for result in changed]
            sensitivity.append(SensitivityResult(dimension, len(changed), disagreement_rate, magnitude_failure_rate, median(deltas) if deltas else None))

        sensitivity.sort(key=lambda item: (-(item.magnitude_failure_rate or 0.0), -item.disagreement_rate, -(item.median_absolute_effect_delta or 0.0), item.dimension))
        return RobustnessReport(claim, original, results, direction_stability, direction_counts, magnitude_stability, magnitude_threshold, self.magnitude_policy, tuple(sensitivity))
