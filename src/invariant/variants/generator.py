from __future__ import annotations

from collections.abc import Callable
from itertools import product

from invariant.core.models import AnalysisSpecification, DecisionSpace

Constraint = Callable[[AnalysisSpecification], bool]


class VariantLimitExceeded(ValueError):
    """Raised when a decision space is larger than the configured safety budget."""


class VariantGenerator:
    def __init__(self, max_variants: int = 256) -> None:
        if max_variants <= 0:
            raise ValueError("max_variants must be > 0")
        self.max_variants = max_variants

    def generate(
        self,
        space: DecisionSpace,
        constraints: tuple[Constraint, ...] = (),
    ) -> tuple[AnalysisSpecification, ...]:
        theoretical_size = len(set(space.churn_days)) * len(set(space.min_orders))
        if theoretical_size > self.max_variants:
            raise VariantLimitExceeded(
                f"decision space contains {theoretical_size} combinations; "
                f"limit is {self.max_variants}"
            )

        variants: dict[str, AnalysisSpecification] = {}
        for churn_days, min_orders in product(
            sorted(set(space.churn_days)),
            sorted(set(space.min_orders)),
        ):
            candidate = AnalysisSpecification(churn_days=churn_days, min_orders=min_orders)
            if all(constraint(candidate) for constraint in constraints):
                variants[candidate.variant_id] = candidate

        return tuple(variants[key] for key in sorted(variants))
