from __future__ import annotations

from invariant.core.models import AnalysisSpecification, DecisionSpace
from invariant.discovery.models import DiscoveryResult, SemanticMetadata


class ChoiceDiscovery:
    """Conservative deterministic discovery from explicit semantic metadata."""

    def discover(self, original: AnalysisSpecification, metadata: SemanticMetadata) -> DiscoveryResult:
        choices = {
            ("churn_days", original.churn_days),
            ("min_orders", original.min_orders),
            *(("churn_days", value) for value in metadata.inactivity_thresholds),
            *(("min_orders", value) for value in metadata.minimum_order_populations),
        }
        churn_days = tuple(sorted(value for name, value in choices if name == "churn_days"))
        min_orders = tuple(sorted(value for name, value in choices if name == "min_orders"))
        return DiscoveryResult(DecisionSpace(churn_days, min_orders), frozenset(choices))
