from __future__ import annotations

from invariant.core.models import (
    AnalysisResult,
    AnalysisSpecification,
    Claim,
    RobustnessReport,
    SensitivityResult,
)
from invariant.execution.base import AnalysisExecutor


def _changed_dimensions(
    original: AnalysisSpecification,
    candidate: AnalysisSpecification,
) -> tuple[str, ...]:
    dimensions: list[str] = []
    if original.churn_days != candidate.churn_days:
        dimensions.append("churn_days")
    if original.min_orders != candidate.min_orders:
        dimensions.append("min_orders")
    return tuple(dimensions)


class RobustnessEvaluator:
    def __init__(self, executor: AnalysisExecutor) -> None:
        self.executor = executor

    def evaluate(
        self,
        claim: Claim,
        original_specification: AnalysisSpecification,
        variants: tuple[AnalysisSpecification, ...],
    ) -> RobustnessReport:
        by_id = {item.variant_id: item for item in variants}
        by_id[original_specification.variant_id] = original_specification
        ordered_specs = tuple(by_id[key] for key in sorted(by_id))

        results = tuple(self.executor.execute(specification) for specification in ordered_specs)
        result_by_id = {result.variant_id: result for result in results}
        original = result_by_id[original_specification.variant_id]

        same_direction = sum(result.direction == original.direction for result in results)
        stability = same_direction / len(results)

        direction_counts = {
            direction: sum(result.direction == direction for result in results)
            for direction in ("negative", "neutral", "positive")
        }

        sensitivity: list[SensitivityResult] = []
        for dimension in ("churn_days", "min_orders"):
            changed = [
                result
                for result in results
                if dimension in _changed_dimensions(original_specification, result.specification)
            ]
            disagreement_rate = (
                sum(result.direction != original.direction for result in changed) / len(changed)
                if changed
                else 0.0
            )
            sensitivity.append(
                SensitivityResult(
                    dimension=dimension,
                    changed_variants=len(changed),
                    disagreement_rate=disagreement_rate,
                )
            )

        sensitivity.sort(key=lambda item: (-item.disagreement_rate, item.dimension))

        return RobustnessReport(
            claim=claim,
            original=original,
            results=results,
            direction_stability=stability,
            direction_counts=direction_counts,
            sensitivity=tuple(sensitivity),
        )
