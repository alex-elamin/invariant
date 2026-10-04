from invariant.core.models import AnalysisSpecification
from invariant.discovery.benchmark import evaluate_discovery
from invariant.discovery.engine import ChoiceDiscovery
from invariant.discovery.models import SemanticMetadata


def test_discovery_is_deterministic_and_preserves_original() -> None:
    original = AnalysisSpecification(30, 1)
    metadata = SemanticMetadata((90, 30, 60, 60), (4, 2, 1))
    first = ChoiceDiscovery().discover(original, metadata)
    second = ChoiceDiscovery().discover(original, metadata)
    assert first == second
    assert first.decision_space.churn_days == (30, 60, 90)
    assert first.decision_space.min_orders == (1, 2, 4)


def test_controlled_discovery_benchmark_scores_known_choices() -> None:
    original = AnalysisSpecification(30, 1)
    result = ChoiceDiscovery().discover(original, SemanticMetadata((30, 60, 90), (1, 2, 4)))
    expected = frozenset({("churn_days", 30), ("churn_days", 60), ("churn_days", 90), ("min_orders", 1), ("min_orders", 2), ("min_orders", 4)})
    metrics = evaluate_discovery(result, expected)
    assert metrics.precision == metrics.recall == metrics.f1 == 1.0
